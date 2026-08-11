`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 08/11/2026 12:23:44 PM
// Design Name: 
// Module Name: shif_reg_34
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


module shif_reg_34(
    input               clk, 
    input               rstn, 
    input         [33:0] para_in, 
    input                para_en, 
    input            scan_enable,
    
    output       [33:0] SR34_out,
    output          shift_out    
    );
    
    
    reg [33:0] shift_reg;
    
    always @(posedge clk or negedge rstn)
    begin 
        if(!rstn)
        begin 
            shift_reg <= 0;
        end
        else
        begin 
            if (para_en)
            begin
                shift_reg <= para_in;
            end
            else if (scan_enable)
            begin
                shift_reg <= {shift_reg[32:0], 1'b0};
            end
       
        end
    
    end
    
    
    assign shift_out = shift_reg[33];
    
    assign SR34_out = shift_reg;
    
endmodule
