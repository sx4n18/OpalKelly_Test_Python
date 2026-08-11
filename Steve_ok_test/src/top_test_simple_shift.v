`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 08/11/2026 11:48:54 AM
// Design Name: 
// Module Name: top_test_simple_shift
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


module top_test_simple_shift(
input  wire [4:0]   okUH,
	output wire [2:0]   okHU,
	inout  wire [31:0]  okUHU,
	inout  wire         okAA,

	input  wire         sys_clkp,
	input  wire         sys_clkn,
	
	// FPGA output to chip to drive Steve's circuits
	
	output             shif_data,
	output             shif_clk, 
	output             samp_hold
	
	
    );
    
    
    
wire rstn_ok;   
    
// Clock solution
wire sys_clk; // 200 MHZ CLOCK WITH PERIOD OF 5 ns
IBUFGDS osc_clk(.O(sys_clk), .I(sys_clkp), .IB(sys_clkn));  
    
wire clk_20m;
// clock divider to generate 20mhz clock
CLK_DIVIDER divider_inst (
    .FASTCLK(sys_clk),
    .rstn(rstn_ok),
    .SLOWCLK(clk_20m)
);
    

// Shift scan register

wire [33:0] para_in34;
wire para_enable;
wire SR34_SE;

wire [33:0] SR34_out_to_ep;

shif_reg_34 SR34 (
                   .clk(clk_20m), 
                   .rstn(rstn_ok), 
                   .para_in(para_in34), 
                    .para_en(para_enable), 
                .scan_enable(SR34_SE),
    
               .SR34_out(SR34_out_to_ep),
              .shift_out(shif_data)  // data coming out of the parallel shift registers  
    );




// OK testing infrastructure 

// Instantiate the okHost and connect endpoints.
wire [65*2-1:0]  okEHx;
wire okClk;
wire [112:0] okHE;
wire [64:0]  okEH;


// endpoint wires
wire [31:0] ep00wire; // wire in end points at 0x00
wire [31:0] ep01wire; // wire in end points at 0x01

wire [31:0] ep20wire; // wire out end points at 0x20
wire [31:0] ep21wire; // wire out end points at 0x21

wire [31:0] ep40trigger; // trigger in end points at 0x40



// ep wires assignment
// WireIn 0x00
//
// [31:0]  para_in34 [31:0]

// WireIn 0x01
//
// [1:0]  para_in34 [33:32]   
// [2]    samp_hold
// [3]    rstn_ok


// WireOut 0x20
//
// [31:0]  SR34_out_to_ep[31:0]

// WireOut 0x21
//
// [1:0]   SR34_out_to_ep[33:32]

// TriggerIn 0x40
//
// [0]    shif_clk
// [1]    SR34_SE
// [2]    para_enable


assign para_in34 [31:0]  =  ep00wire;

assign para_in34 [33:32] = ep01wire[1:0];

assign samp_hold  = ep01wire[2];

assign  rstn_ok = ep01wire[3];



assign ep20wire = SR34_out_to_ep[31:0];

assign ep21wire = {30'b0, SR34_out_to_ep[33:32]};



assign shif_clk = ep40trigger[0];

assign SR34_SE =  ep40trigger[1];

assign para_enable =  ep40trigger[2];



okHost okHI(
	.okUH(okUH),
	.okHU(okHU),
	.okUHU(okUHU),
	.okAA(okAA),
	.okClk(okClk),
	.okHE(okHE), 
	.okEH(okEH)
);

okWireOR # (.N(2)) wireOR (okEH, okEHx);

okWireIn     wi00(.okHE(okHE),                             .ep_addr(8'h00), .ep_dataout(ep00wire));
okWireIn     wi01(.okHE(okHE),                             .ep_addr(8'h01), .ep_dataout(ep01wire));
okWireOut    wo20(.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(ep20wire));
okWireOut    wo21(.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h21), .ep_datain(ep21wire));
okTriggerIn  ti40(.okHE(okHE),                             .ep_addr(8'h40), .ep_clk(clk_20m), .ep_trigger(ep40trigger));

    
endmodule
