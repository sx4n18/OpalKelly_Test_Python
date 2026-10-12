`timescale 1ns / 1ps
///////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date:
// Design Name:
// Module Name: SPI_test_master
// Project Name:
// Target Devices:
// Tool Versions:
// Description:
//    This is the SPI master that shall take the address and data from the host
//    and send it to the SPI slave. The SPI master shall also receive the data from the
//    SPI slave and send it back to the host. By default the SPI master shall operate in mode 0 (CPOL=0, CPHA=0).


module SPI_test_master(
    input wire clk, // system clock that operates at 20 Mhz
    input wire rst_n, // active low reset
    input wire send_SPI, // start the SPI transaction
    input wire [7:0] addr, // address from host
    input wire [7:0] data_in, // data from host
    output wire [7:0] data_out, // data to host
    output reg done, // done signal to host
    output wire spi_clk, // SPI clock
    output wire spi_mosi, // SPI master out slave in
    input wire spi_miso, // SPI master in slave out
    output wire spi_cs_n // SPI chip select (active low)

);
    reg SPI_CLK_1M;    // this should be a low freq clock at 1 Mhz, generated from the system clock
    reg [15:0] clk_div_cnt; // clock divider counter for generating SPI_CLK_1M
    reg para_load; // signal to load the parallel data into the shift register
    reg shift_en_MOSI, shift_en_MISO; // signal to enable shifting of the MOSI and MISO shift registers
    reg nck_mask; // signal to generate spi_clk from SPI_CLK_1M, we will use a mask to generate the spi_clk
    reg [3:0] curr_state; // state machine state
    reg [3:0] next_state; // next state machine state
    reg [4:0] bit_cnt; // bit counter for SPI transaction
    reg [15:0] shift_reg_mosi; // shift register for SPI transaction
    reg [15:0] shift_reg_miso; // shift register for SPI transaction

    wire SPI_CLK_RISING_EDGE = (SPI_CLK_1M == 1'b1 && clk_div_cnt == 16'h0); // detect the rising edge of SPI_CLK_1M

    // state machine states
    localparam IDLE = 4'b0000;
    localparam LOAD = 4'b0001;
    localparam TRANSFER = 4'b0010;
    localparam DONE = 4'b0011;


    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            curr_state <= 4'b0;
        end else begin
            curr_state <= next_state;
        end
    end

    always @(posedge clk or negedge rst_n) begin // 20 Mhz to 1 mhz, we flip every 10 cycles
        if(!rst_n) begin
            SPI_CLK_1M <= 1'b0;
            clk_div_cnt <= 16'b0;
        end else begin
            if(clk_div_cnt == 16'h1001) begin
                SPI_CLK_1M <= ~SPI_CLK_1M;
                clk_div_cnt <= 16'b0;
            end else begin
                clk_div_cnt <= clk_div_cnt + 1;
            end
        end
    end


    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) begin
            bit_cnt <= 5'b0;
        end else begin

            case(curr_state)

                IDLE: begin

                end

                LOAD: begin

                end

                TRANSFER: begin
                    if(SPI_CLK_RISING_EDGE && bit_cnt < 5'd16) begin
                        bit_cnt <= bit_cnt + 1;
                    end

                end

                DONE: begin
                    bit_cnt <= 5'b0;
                end
            endcase
        end
    end


    always @(*) begin
        next_state = curr_state;
        para_load = 1'b0;
        shift_en_MOSI = 1'b0;
        shift_en_MISO = 1'b0;
        nck_mask = 1'b0;
        done = 1'b1;
        case(curr_state)
            IDLE: begin
                done = 1'b1;        // signal to host that the SPI transaction is done
                if(send_SPI) begin
                    next_state = LOAD;
                end
            end

            LOAD: begin
                para_load = 1'b1;
                if(SPI_CLK_1M == 1'b0 && clk_div_cnt < 16'h8) begin // get to next state when spi_clk_1m is low, and also the div counter is smaller than 8 to leave some time for the shift register to load the data
                    next_state = TRANSFER;
                end

            end

            TRANSFER: begin
                shift_en_MOSI = 1'b1;
                shift_en_MISO = 1'b1;
                nck_mask = 1'b1;
                if(SPI_CLK_1M == 1'b0 && bit_cnt == 5'd16 && clk_div_cnt >= 16'h3) begin // jump to finish when SPI_CLK_1M is low, bit counter is 15, and the clk_div_cnt is bigger than 3 to leave some time for the last bit to be shifted out
                    next_state = DONE;
                end
            end

            DONE: begin
                next_state = IDLE;
            end

        endcase
    end

    // MOSI chain, we shift the data in on the falling edge of SPI_CLK_1M
    always @(negedge SPI_CLK_1M or negedge rst_n) begin
        if(!rst_n) begin
            shift_reg_mosi <= 16'b0;
        end else begin
            if(para_load) begin
                shift_reg_mosi <= {addr, data_in};
            end else if(shift_en_MOSI) begin
                shift_reg_mosi <= {shift_reg_mosi[14:0], 1'b0};
            end
        end
    end

    // MISO chain, we shift the data out on the rising edge of SPI_CLK_1M
    always @(posedge SPI_CLK_1M or negedge rst_n) begin
        if(!rst_n) begin
            shift_reg_miso <= 16'b0;
        end else begin
            if(shift_en_MISO) begin
                shift_reg_miso <= {shift_reg_miso[14:0], spi_miso};
            end
        end
    end

    // assign the outputs
    assign spi_clk = SPI_CLK_1M & nck_mask; // spi_clk is generated from SPI_CLK_1M and the mask
    assign spi_mosi = shift_reg_mosi[15]; // the MSB of the shift register is the output to the SPI slave
    assign spi_cs_n = (curr_state == IDLE) ? 1'b1 : 1'b0; // chip select is active low
    assign data_out = shift_reg_miso[7:0]; // the lower 8 bits of the shift register is the data to the host

endmodule