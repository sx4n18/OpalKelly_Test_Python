`timescale 1ns / 1ps
///////////////////////////////////////////////////////////////////////////////////
// Module Name: SPI_test_master
// Description:
//    SPI master, mode 0 (CPOL=0, CPHA=0), 16-bit frame {addr, data_in}, MSB first.
//    The last 8 bits received on MISO are returned on data_out.
//
//    Everything runs in the single system-clock domain. The SPI clock is a
//    registered output toggled by a clock-enable "tick" -- no logic is clocked
//    by the divided clock.
//
//    Timing (defaults, clk = 20 MHz, HALF_PERIOD = 10):
//      SCK = 20 MHz / (2*10) = 1 MHz, 50 % duty
//      CS_n low -> first SCK rise : 1 half period (500 ns)
//      last SCK fall -> CS_n high : 1 half period (500 ns)
//
//    Handshake:
//      done is high while idle. Pulse send_SPI (1 clk) while done is high to
//      start a transfer. done drops the next cycle and returns high when the
//      frame is finished; data_out is valid from that cycle until the next
//      transfer completes. If send_SPI is held high, transfers repeat back to
//      back with CS_n high for only one clk cycle in between.
//      send_SPI must be synchronous to clk.
///////////////////////////////////////////////////////////////////////////////////

module SPI_test_master #(
    parameter integer HALF_PERIOD = 10      // clk cycles per half SCK period
)(
    input  wire       clk,       // system clock, 20 MHz
    input  wire       rst_n,     // active-low async reset
    input  wire       send_SPI,  // start a transaction (sampled while idle)
    input  wire [7:0] addr,      // address from host
    input  wire [7:0] data_in,   // data from host
    output wire [7:0] data_out,  // data to host (valid when done is high)
    output reg        done,      // high = idle / previous transfer finished
    output wire       spi_clk,   // SPI clock
    output wire       spi_mosi,  // master out, slave in
    input  wire       spi_miso,  // master in, slave out
    output wire       spi_cs_n   // chip select, active low
);

    localparam [1:0] IDLE     = 2'd0,
                     TRANSFER = 2'd1,
                     DONE     = 2'd2;

    reg [1:0]  state;
    reg [15:0] div_cnt;
    reg [4:0]  bit_cnt;
    reg [15:0] shift_reg_mosi;
    reg [15:0] shift_reg_miso;
    reg [7:0]  rx_data;
    reg        sclk_r;
    reg        cs_n_r;

    wire tick = (div_cnt == HALF_PERIOD - 1);   // one half SCK period elapsed

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state          <= IDLE;
            div_cnt        <= 16'd0;
            bit_cnt        <= 5'd0;
            shift_reg_mosi <= 16'd0;
            shift_reg_miso <= 16'd0;
            rx_data        <= 8'd0;
            sclk_r         <= 1'b0;
            cs_n_r         <= 1'b1;
        end else begin
            case (state)
                IDLE: begin
                    sclk_r  <= 1'b0;
                    cs_n_r  <= 1'b1;
                    div_cnt <= 16'd0;
                    bit_cnt <= 5'd0;
                    if (send_SPI) begin
                        shift_reg_mosi <= {addr, data_in};  // bit 15 on MOSI immediately
                        cs_n_r         <= 1'b0;
                        state          <= TRANSFER;
                    end
                end

                TRANSFER: begin
                    if (tick) begin
                        div_cnt <= 16'd0;
                        if (!sclk_r) begin
                            // rising edge: sample MISO
                            sclk_r         <= 1'b1;
                            shift_reg_miso <= {shift_reg_miso[14:0], spi_miso};
                            bit_cnt        <= bit_cnt + 5'd1;
                        end else begin
                            // falling edge: present next MOSI bit, or finish
                            sclk_r <= 1'b0;
                            if (bit_cnt == 5'd16)
                                state <= DONE;
                            else
                                shift_reg_mosi <= {shift_reg_mosi[14:0], 1'b0};
                        end
                    end else begin
                        div_cnt <= div_cnt + 16'd1;
                    end
                end

                DONE: begin
                    // hold CS low for half a period after the last falling edge
                    if (tick) begin
                        div_cnt <= 16'd0;
                        cs_n_r  <= 1'b1;
                        rx_data <= shift_reg_miso[7:0];
                        state   <= IDLE;
                    end else begin
                        div_cnt <= div_cnt + 16'd1;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

    always @(*) done = (state == IDLE);

    assign spi_clk  = sclk_r;
    assign spi_mosi = shift_reg_mosi[15];
    assign spi_cs_n = cs_n_r;
    assign data_out = rx_data;

endmodule
