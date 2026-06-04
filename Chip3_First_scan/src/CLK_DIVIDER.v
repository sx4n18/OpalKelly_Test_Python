`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05/20/2026 05:16:08 PM
// Design Name: 
// Module Name: CLK_DIVIDER
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


module CLK_DIVIDER(
    input FASTCLK,
    input rstn,
    output reg SLOWCLK
    );
    
    parameter DIV_PARAM = 10;
    
    reg [3:0] cnt;
    
    always @(posedge FASTCLK or negedge rstn)
    begin
        if (!rstn)
        begin 
            SLOWCLK <= 0; 
            cnt <= 0;
        end
        else if (cnt == (DIV_PARAM>>1)-1)
            begin
            cnt <= 0;
            SLOWCLK <= ~SLOWCLK;
           end
        else 
           cnt <= cnt +1;
    end
    
    
endmodule
