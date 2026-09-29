`timescale 1ns / 1ps

///////////////////////////////////////////////////////////////////////////////////
// This is a simple parameterised shift register module that can be used to create
// the Parallel-In Serial-Out (PISO) shift register.
// The width of the shift register can be set using the parameter WIDTH.
///////////////////////////////////////////////////////////////////////////////////

module para_shift_reg #(
    parameter WIDTH = 8
)(
    input wire clk,
    input wire rst_n,
    input wire load,
    input wire [WIDTH-1:0] parallel_in,
    input wire shift_enable,
    output reg [WIDTH-1:0] shift_reg,
    output  serial_out
);



    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg <= 0;
        end else if (load) begin
            shift_reg <= parallel_in;
        end else if (shift_enable) begin
            shift_reg <= {1'b0, shift_reg[WIDTH-1:1]}; // Shift right and fill with 0
        end
    end

    assign serial_out = shift_reg[0];    // Output the least significant bit

    endmodule