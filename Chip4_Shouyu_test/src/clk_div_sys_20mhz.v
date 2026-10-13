`timescale 1ns / 1ps

module clk_div_sys_20mhz(
    input wire sys_clk, // 200 MHz clock
    input wire rst_n, // active low reset
    output reg clk_out // 20 MHz clock
    );

    reg [2:0] cnt; // 3-bit counter

    always @(posedge sys_clk or negedge rst_n) begin
        if (!rst_n) begin
            cnt <= 0;
            clk_out <= 0;
        end else begin
            if (cnt == 3'd5) begin // flip clk_out every 5 sys_clk cycles (200 MHz / 5 = 40 MHz, then divide by 2 for 20 MHz)
                cnt <= 0;
                clk_out <= ~clk_out; // Toggle output clock
            end else begin
                cnt <= cnt + 1;
            end
        end
    end

endmodule