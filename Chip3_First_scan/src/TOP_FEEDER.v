`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05/20/2026 04:28:41 PM
// Design Name: 
// Module Name: TOP_FEEDER
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


module TOP_FEEDER(
	input  wire [4:0]   okUH,
	output wire [2:0]   okHU,
	inout  wire [31:0]  okUHU,
	inout  wire         okAA,

	input  wire         sys_clkp,
	input  wire         sys_clkn,
	
	// FPGA output/input between board and chip
	// Shouyu's side
	output         PLL_PDN, 
	output         PLL_TEST,   
	output         FRANGE, 
	output         PLL_NMSX_SEL, 
	output         SDI_to_chip,
	output         SE, 
	
	input          TCKO, 
	input          SDO_from_chip,
	
	// Steve's scan chain
	output         LVDS_ser_data_ctrl,
	output         ctrlB,
	
	// Clock to the chip
	output         PLL_FREF_TCK, 
	output         pll_config_clk, // basically NMSX_TCK
	output         clk_LVDS, 
	
	// board level 
	output [7:0]   XEM7310LED
    );


wire rstn_ok;   
    
  // Clock
wire sys_clk; // 200 MHZ CLOCK WITH PERIOD OF 5 ns
IBUFGDS osc_clk(.O(sys_clk), .I(sys_clkp), .IB(sys_clkn));  
    
wire clk_20m;
CLK_DIVIDER divider_inst (
    .FASTCLK(sys_clk),
    .rstn(rstn_ok),
    .SLOWCLK(clk_20m)
);

// chip scan chain + reference clock to be 20MHZ
assign PLL_FREF_TCK = clk_20m;
assign pll_config_clk = clk_20m;
assign clk_LVDS = clk_20m;

////////////////////////////////////////////////
// internal scan register to feed into the chip

// Following wires should be on the wire in endpoint
wire PARAIN_EN;
wire [11:0] PARA_FEED; 
wire OK_SCAN_IN;

// Following wires should be on the Wire out endpoint
wire OK_SCAN_OUT;
wire [11:0] OK_LED_WIREOUT_EP; // --> boolean logic of internal register values

// Following wires should be on trigger in endpoint
wire OK_SCAN_ENABLE;

scan_chain_feeder  SCAN_UNIT(
     .clk20m(clk_20m),
     .rst_n(rstn_ok),
      .paraIn_Enable(PARAIN_EN), 
     .ParaFeed(PARA_FEED), 

      .SE(OK_SCAN_ENABLE),
     .scan_in(OK_SCAN_IN),
    
     .internal_reg_LED(OK_LED_WIREOUT_EP),

     .scan_out(OK_SCAN_OUT)
        
    );
    
assign SDI_to_chip = OK_SCAN_OUT;

////////////////////////////////////////////////
// function

// function definition
function [11:0] xem7310_led;
input [11:0] a;
integer i;
begin
	for(i=0; i<12; i=i+1) begin: u
		xem7310_led[i] = (a[i]==1'b1) ? (1'b0) : (1'bz);
	end
end
endfunction

// to FPGA LED

wire [11:0] OK_LED; // converted LED logic : 0 --> lit, z --> off

assign OK_LED =  xem7310_led(OK_LED_WIREOUT_EP);
assign XEM7310LED = OK_LED[7:0];


////////////////////////////////////////////////////
// Opal kelly endpoints host instrantiations

// Instantiate the okHost and connect endpoints.
wire [65*1-1:0]  okEHx;
wire okAA, okClk;
wire [112:0] okHE;
wire [64:0]  okEH;


// endpoint wires
wire [31:0] ep00wire; // wire in end points at 0x00
wire [31:0] ep20wire; // wire out end points at 0x20
wire [31:0] ep40wire; // trigger in end points at 0x40

// wire in signals
assign rstn_ok      = ep00wire[14];
assign OK_SCAN_IN   = ep00wire[13];
assign PARAIN_EN    = ep00wire[12];
assign PARA_FEED    = ep00wire[11:0]; 
assign PLL_PDN      = ep00wire[15];
assign PLL_TEST     = ep00wire[16];
assign FRANGE       = ep00wire[17];
assign PLL_NMSX_SEL = ep00wire[18];
assign LVDS_ser_data_ctrl = ep00wire[19];
assign ctrlB        = ep00wire[20];

// wire out signals

assign ep20wire = {18'b0000,OK_SCAN_OUT,SDO_from_chip,OK_LED_WIREOUT_EP}; //18,1,1,12 => 32 bits

// trigger in signals

assign OK_SCAN_ENABLE = ep40wire[0]; // scan enable for the Opal kelly scan chain
assign SE = ep40wire[1]; // scan enable for the chip

okHost okHI(
	.okUH(okUH),
	.okHU(okHU),
	.okUHU(okUHU),
	.okAA(okAA),
	.okClk(okClk),
	.okHE(okHE), 
	.okEH(okEH)
);

okWireOR # (.N(1)) wireOR (okEH, okEHx);

okWireIn     wi00(.okHE(okHE),                             .ep_addr(8'h00), .ep_dataout(ep00wire));
okWireOut    wo20(.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(ep20wire));
okTriggerIn  ti40(.okHE(okHE),                             .ep_addr(8'h40), .ep_clk(clk_20m), .ep_trigger(ep40wire));


  
    
endmodule
