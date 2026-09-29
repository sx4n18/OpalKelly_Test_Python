`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date:
// Design Name:
// Module Name: Steve_SPI_ctrl
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

module Steve_SPI_ctrl(
    input  wire [4:0]   okUH,
	output wire [2:0]   okHU,
	inout  wire [31:0]  okUHU,
	inout  wire         okAA,

	input  wire         sys_clkp,
	input  wire         sys_clkn,

	// FPGA output/input between board and chip
    output              spi_clk,
    output  reg         MOSI,
    output              nCS,
    output              nglobals,
    output              nclk_set,
    output              node_sw,
    output              Latch,
    output              SH



);

///////////////////////////  clk ///////////////////////////////

// opalkelly reset
wire ok_rstn;       // this will be a controllable wire in bit


// Clock
wire sys_clk; // 200 MHZ CLOCK WITH PERIOD OF 5 ns
wire clk5mhz; // 5 MHz clock for opalkelly and SPI

IBUFGDS osc_clk(.O(sys_clk), .I(sys_clkp), .IB(sys_clkn));

// clock divider to produce 5 MHz clock for SPI
clk_div_sys_5mhz clk_div_inst(
    .sys_clk(sys_clk),
    .rst_n(ok_rstn),
    .clk_out(clk5mhz)
);



/////////////////////////// shift registers for each group  ///////////////////////////////

wire para_load;         // this will be a controllable wire in bit, shared by all shft registers

// range [2:0] settings
wire [2:0] parallel_data_range; // 3-bit parallel data input for range
wire SE0;                       // control signal to right shift data for range, this will be a controllable TriggerIn
wire [2:0] shift_reg_range_out; // 3-bit shift register output for loaded range, this will be a monitored WireOut
wire range_MOSI;                 // serial output for SPI for range, this will be muxed to the MOSI pin


// Instantiate the parameterized shift register for range
para_shift_reg #(
    .WIDTH(3)
) shift_reg_range (
    .clk(clk5mhz),
    .rst_n(ok_rstn),
    .load(para_load), // control signal to load parallel data
    .parallel_in(parallel_data_range), // 3-bit parallel data input
    .shift_enable(SE0), // control signal to shift data
    .shift_reg(shift_reg_range_out), // 3-bit shift register output
    .serial_out(range_MOSI) // serial output for SPI
);


// Addr [9:0] cfg
wire [9:0] parallel_data_addr; // 10-bit parallel data input for addr
wire SE1;                       // control signal to right shift data for addr, this will be a controllable TriggerIn
wire [9:0] shift_reg_addr_out; // 10-bit shift register output for loaded addr, this will be a monitored WireOut
wire addr_MOSI;                 // serial output for SPI for addr, this will be muxed to the MOSI pin

// Instantiate the parameterized shift register for addr
para_shift_reg #(
    .WIDTH(10)
) shift_reg_addr (
    .clk(clk5mhz),
    .rst_n(ok_rstn),
    .load(para_load), // control signal to load parallel data
    .parallel_in(parallel_data_addr), // 10-bit parallel data input
    .shift_enable(SE1), // control signal to shift data
    .shift_reg(shift_reg_addr_out), // 10-bit shift register output
    .serial_out(addr_MOSI) // serial output for SPI
);

// clkcfg [2:0]
wire nine_eight_cfg;
wire en_adc_res_cfg;
wire clk_doub_cfg;
wire [2:0] parallel_data_clkcfg; // 3-bit parallel data input for clkcfg
wire SE2;
wire [2:0] shift_reg_clkcfg_out;
wire clkcfg_MOSI;

assign parallel_data_clkcfg = {nine_eight_cfg, en_adc_res_cfg, clk_doub_cfg};

// instantiate the parameterized shift register for clkcfg
para_shift_reg #(
    .WIDTH(3)
) shift_reg_clkcfg (
    .clk(clk5mhz),
    .rst_n(ok_rstn),
    .load(para_load), // control signal to load parallel data
    .parallel_in(parallel_data_clkcfg), // 3-bit parallel data input
    .shift_enable(SE2), // control signal to shift data
    .shift_reg(shift_reg_clkcfg_out), // 3-bit shift register output
    .serial_out(clkcfg_MOSI) // serial output for SPI
);


// node specific cfg [9:0]
wire [4:0] offset_cfg;
wire en_offset_amp_cfg;
wire FixRef_cfg;
wire en_general_cfg;
wire offctrl_cfg;
wire Autohold_cfg;
wire [9:0] parallel_data_nodecfg; // 10-bit parallel data input for nodecfg
wire SE3;
wire [9:0] shift_reg_nodecfg_out;
wire nodecfg_MOSI;

assign parallel_data_nodecfg = {offset_cfg, en_offset_amp_cfg, FixRef_cfg, en_general_cfg, offctrl_cfg, Autohold_cfg};

// instantiate the parameterized shift register for nodecfg
para_shift_reg #(
    .WIDTH(10)
) shift_reg_nodecfg (
    .clk(clk5mhz),
    .rst_n(ok_rstn),
    .load(para_load), // control signal to load parallel data
    .parallel_in(parallel_data_nodecfg), // 10-bit parallel data input
    .shift_enable(SE3), // control signal to shift data
    .shift_reg(shift_reg_nodecfg_out), // 10-bit shift register output
    .serial_out(nodecfg_MOSI) // serial output for SPI
);

/////////////////////////// mux out for mosi  ///////////////////////////////

wire [1:0] mosi_sel; // 2-bit control signal to select which shift register's serial output to send to MOSI, this will be a controllable wire in bit

always @(*) begin
    case (mosi_sel)
        2'b00: MOSI = range_MOSI;
        2'b01: MOSI = addr_MOSI;
        2'b10: MOSI = clkcfg_MOSI;
        2'b11: MOSI = nodecfg_MOSI;
        default: MOSI = 1'b0; // default case
    endcase
end

/////////////////////////// opalkelly end point design ///////////////////////////////
// WireIn 0x00:
// [2:0] parallel_data_range
// [3]   nglobals
// -----------------
// [4]   para_load     system infra signals
// [5]   ok_rstn
// [7:6] mosi_sel
// [8]   Latch
// [9]   SH
// -----------------
// WireIn 0x01:
// [9:0] parallel_data_addr
// [10]  nCS
// WireIn 0x02:
// [2] nine_eight_cfg
// [1] en_adc_res_cfg
// [0] clk_doub_cfg
// [3] nclk_set
// WireIn 0x03:
// [0] AutoHold_cfg
// [1] offctrl_cfg
// [2] en_general_cfg
// [3] FixRef_cfg
// [4] en_offset_amp_cfg
// [9:5] offset_cfg
// [10] node_sw
//
// WireOut 0x20:
// [2:0] shift_reg_range_out
// WireOut 0x21:
// [9:0] shift_reg_addr_out
// WireOut 0x22:
// [2:0] shift_reg_clkcfg_out
// WireOut 0x23:
// [9:0] shift_reg_nodecfg_out
//
// TriggerIn 0x40:
// [0] SE0
// [1] SE1
// [2] SE2
// [3] SE3
// [4] spi_clk


// Instantiate the okHost and connect endpoints.
wire [65*4-1:0]  okEHx;
wire okClk;
wire [112:0] okHE;
wire [64:0]  okEH;

// endpoint wires
wire [31:0] ep00wire; // wire in end points at 0x00
wire [31:0] ep01wire; // wire in end points at 0x01
wire [31:0] ep02wire; // wire in end points at 0x02
wire [31:0] ep03wire; // wire in end points at 0x03
wire [31:0] ep20wire; // wire out end points at 0x20
wire [31:0] ep21wire; // wire out end points at 0x21
wire [31:0] ep22wire; // wire out end points at 0x22
wire [31:0] ep23wire; // wire out end points at 0x23
wire [31:0] ep40trigger; // trigger in end points at 0x40

// WireIn 0x00
assign parallel_data_range = ep00wire[2:0];
assign nglobals = ep00wire[3];
assign para_load = ep00wire[4];
assign ok_rstn = ep00wire[5];
assign mosi_sel = ep00wire[7:6];
assign Latch = ep00wire[8];
assign SH = ep00wire[9];

// WireIn 0x01
assign parallel_data_addr = ep01wire[9:0];
assign nCS = ep01wire[10];

// WireIn 0x02
assign nine_eight_cfg = ep02wire[2];
assign en_adc_res_cfg = ep02wire[1];
assign clk_doub_cfg = ep02wire[0];
assign nclk_set = ep02wire[3];

// WireIn 0x03
assign Autohold_cfg = ep03wire[0];
assign offctrl_cfg = ep03wire[1];
assign en_general_cfg = ep03wire[2];
assign FixRef_cfg = ep03wire[3];
assign en_offset_amp_cfg = ep03wire[4];
assign offset_cfg = ep03wire[9:5];
assign node_sw = ep03wire[10];

// WireOut 0x20
assign ep20wire[2:0] = shift_reg_range_out;
// WireOut 0x21
assign ep21wire[9:0] = shift_reg_addr_out;
// WireOut 0x22
assign ep22wire[2:0] = shift_reg_clkcfg_out;
// WireOut 0x23
assign ep23wire[9:0] = shift_reg_nodecfg_out;

// TriggerIn 0x40
assign SE0 = ep40trigger[0];
assign SE1 = ep40trigger[1];
assign SE2 = ep40trigger[2];
assign SE3 = ep40trigger[3];
assign spi_clk = ep40trigger[4];

// Instantiate the okHost and connect endpoints.
okHost okHI(
    .okUH(okUH),
    .okHU(okHU),
    .okUHU(okUHU),
    .okAA(okAA),
    .okClk(okClk),
    .okHE(okHE),
    .okEH(okEH)
);

// Instantiate the endpoints
okWireOR # (.N(4)) wireOR (okEH, okEHx);

okWireIn     wi00(.okHE(okHE), .ep_addr(8'h00), .ep_dataout(ep00wire));
okWireIn     wi01(.okHE(okHE), .ep_addr(8'h01), .ep_dataout(ep01wire));
okWireIn     wi02(.okHE(okHE), .ep_addr(8'h02), .ep_dataout(ep02wire));
okWireIn     wi03(.okHE(okHE), .ep_addr(8'h03), .ep_dataout(ep03wire));
okWireOut    wo20(.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(ep20wire));
okWireOut    wo21(.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h21), .ep_datain(ep21wire));
okWireOut    wo22(.okHE(okHE), .okEH(okEHx[ 2*65 +: 65 ]), .ep_addr(8'h22), .ep_datain(ep22wire));
okWireOut    wo23(.okHE(okHE), .okEH(okEHx[ 3*65 +: 65 ]), .ep_addr(8'h23), .ep_datain(ep23wire));
okTriggerIn  ti40(.okHE(okHE), .ep_addr(8'h40), .ep_clk(clk5mhz), .ep_trigger(ep40trigger));





endmodule