`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05/11/2026 04:14:34 PM
// Design Name: 
// Module Name: NAND_2x1
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module NAND_2x1(
    input A, 
    input B, 
    output O 
    );
    
    
    
    assign O = ~(A&B);
    
    
endmodule
