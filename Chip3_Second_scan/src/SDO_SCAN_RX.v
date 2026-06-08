`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/08/2026 01:31:29 PM
// Design Name: 
// Module Name: SDO_SCAN_RX
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


module SDO_SCAN_RX(
        input           clk, 
        input           SE, 
        input           scan_in, 
        
        output          scan_out,
        output  [11:0]  PARA_DAT

    );
    
    reg [11:0] scan_reg;
    
    always @(posedge clk)
    begin
        if(SE)
        scan_reg <= {scan_reg[10:0], scan_in};
    end
    
    
    assign PARA_DAT =  scan_reg;
    assign scan_out =  scan_reg[11];
    
endmodule
