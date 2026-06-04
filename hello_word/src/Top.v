`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05/11/2026 04:15:38 PM
// Design Name: 
// Module Name: Top
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


module Top(

    input   [4:0] okUH, 
    output  [2:0] okHU, 
    inout   [31:0] okUHU, 
    inout           okAA, 
    
    
    
    output  led

    );
    
    wire WireInA, WireInB;
    
    wire [112:0] okHostEP;
    wire [31:0] ep00wire;
    wire [31:0] ep01wire;
    
    
    wire okClk,LEDWIRE;
    
    
    assign WireInA = ep00wire[0];
    assign WireInB = ep01wire[0];
    
    okHost  okHOSTTOP
	(
	.okUH(okUH),
	.okHU(okHU),
	.okUHU(okUHU),
	.okAA(okAA),
	.okClk(okClk),
    .okHE(okHostEP)
	
	);
    
    
    
    
    
    okWireIn    EP00 (.okHE(okHostEP),                             .ep_addr(8'h00), .ep_dataout(ep00wire));
    okWireIn    EP01 (.okHE(okHostEP),                             .ep_addr(8'h01), .ep_dataout(ep01wire));
    
    // wire [65*2-1:0]  okEHx;
    // okWireOR # (.N(2)) wireOR (okEH, okEHx);
    // okWireOut    ep20 (.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(ep20wire));
    // okWireOut    ep21 (.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h21), .ep_datain(ep21wire));
    
    
    NAND_2x1 simple_nand(
        .A(WireInA),
        .B(WireInB), 
        .O(LEDWIRE)
    );
    
    
    assign led = LEDWIRE ? 1'b0 : 1'bz;
    
    
endmodule
