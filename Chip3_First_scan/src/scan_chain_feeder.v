`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05/20/2026 04:02:56 PM
// Design Name: 
// Module Name: scan_chain_feeder
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


module scan_chain_feeder(
    input clk20m,
    input rst_n,
    input  paraIn_Enable, 
    input [11:0] ParaFeed, 
    
    input  SE,
    input scan_in,
    
    output [11:0] internal_reg_LED,
    
    output scan_out
        
    );
    
    
    reg [11:0] Temp_feed_reg;
 
 


always @(posedge clk20m or negedge rst_n)
begin
    if (!rst_n)
    begin 
        Temp_feed_reg <= 12'b0000_0000_0000;
    end
    else // read in the Wire value into the registers
    if(paraIn_Enable)
    begin 
        Temp_feed_reg <= ParaFeed;
    end
    else // shift~~~
    if (SE)
    begin 
        Temp_feed_reg <= {Temp_feed_reg[10:0], scan_in};
    end
end


    
    // assign the FPGA fabric internal register to LED
    assign internal_reg_LED = Temp_feed_reg;
    
    assign scan_out = Temp_feed_reg[11];
    
endmodule
