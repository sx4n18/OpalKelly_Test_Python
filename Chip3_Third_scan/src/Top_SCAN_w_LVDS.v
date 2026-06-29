`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/09/2026 03:04:12 PM
// Design Name: 
// Module Name: Top_SCAN_w_LVDS
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


module Top_SCAN_w_LVDS(
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
	output         clk_LVDS,  // This should be a trigger in
	// LVDS input
	input          outP,        // LVDS P input from chip 
	input          outN,        // LVDS N input from chip
	
	// board level
	output REF_CLK_B35,                  // This is the reference clock to show that testing point works, should swing for 2.5 V
	output div_clk_from_LVDS,            // this is the div clock to be tapped out, should be 1/16 of the LVDS in.
	output [7:0]   XEM7310LED
	
    );
    
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

assign REF_CLK_B35 = clk_20m;
////////////////////////////////////////////////
// Deal with lvds input with bufds 

wire LVDS_OUT; // translated lvds voltage level

IBUFDS #(
        .DIFF_TERM("TRUE"),
        .IOSTANDARD("LVDS_25")
)   rx_buf(
        .I(outP), 
        .IB(outN),
        .O(LVDS_OUT)
);

////////////////////////////////////////////////
// Because the wires have been ripped...I will 
// have to increment internally

reg [31:0] LVDS_REG_CNT;

always @(posedge LVDS_OUT or negedge rstn_ok)
begin
    if(!rstn_ok)
    begin
       LVDS_REG_CNT <= 0; 
    end
    else
    begin
        LVDS_REG_CNT <= LVDS_REG_CNT +1;
    end
end

assign div_clk_from_LVDS = LVDS_REG_CNT[3];

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

assign OK_SCAN_ENABLE = SE;

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

// to FPGA LED

wire [11:0] OK_LED; // converted LED logic : 0 --> lit, z --> off

assign OK_LED =  xem7310_led(OK_LED_WIREOUT_EP);
assign XEM7310LED = OK_LED[7:0];

/////////////////////////////////////////////////////
// Internal scan register to receive the data from SDO

wire [11:0] SDO_PARA_DATA;
wire SDOCAT_SE;

assign SDOCAT_SE = SE;

SDO_SCAN_RX  SDO_CATCHER(
        .clk(clk_20m), 
        .SE(SDOCAT_SE), 
        .scan_in(SDO_from_chip), 
        
        .scan_out(),
        .PARA_DAT(SDO_PARA_DATA));




////////////////////////////////////////////////////
// Opal kelly endpoints host instrantiations

// Instantiate the okHost and connect endpoints.
wire [65*2-1:0]  okEHx;
wire okClk;
wire [112:0] okHE;
wire [64:0]  okEH;


// endpoint wires
wire [31:0] ep00wire; // wire in end points at 0x00
wire [31:0] ep20wire; // wire out end points at 0x20
wire [31:0] ep21wire; // Special wireout for lvds counter end point at 0x21
wire [31:0] ep40wire; // trigger in end points at 0x40

// WireIn 0x00
//
// [11:0]  PARA_FEED
// [12]    PARAIN_EN
// [13]    OK_SCAN_IN
// [14]    rstn_ok
// [15]    PLL_PDN
// [16]    PLL_TEST
// [17]    FRANGE
// [18]    PLL_NMSX_SEL
// [19]    LVDS_ser_data_ctrl
// [20]    ctrlB

// WireOut 0x20
//
// [11:0]   OK_LED_WIREOUT_EP
// [12]     SDO_from_chip
// [13]     OK_SCAN_OUT
// [25:14]  SDO_PARA_DATA
// [31:26]  Reserved

// TriggerIn 0x40
// [0]    SE
// [1]    clk_LVDS

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

assign ep20wire = {
                    6'b000000,          // [31:26]
                    SDO_PARA_DATA,      // [25:14]
                    OK_SCAN_OUT,        // [13]
                    SDO_from_chip,      // [12]
                    OK_LED_WIREOUT_EP}; // [11:0]
                    //6,12,1,1,12 => 32 bits

assign ep21wire = LVDS_REG_CNT;


// trigger in signals

assign SE = ep40wire[0]; // Global scan enable for the Opal kelly scan chain and chip
assign clk_LVDS = ep40wire[1]; // Steve's scan chain clock

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
okWireOut    wo20(.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(ep20wire));
okWireOut    wo21(.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h21), .ep_datain(ep21wire));
okTriggerIn  ti40(.okHE(okHE),                             .ep_addr(8'h40), .ep_clk(clk_20m), .ep_trigger(ep40wire));


endmodule

