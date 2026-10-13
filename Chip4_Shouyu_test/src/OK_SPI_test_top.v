`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//
// Engineer: Shouyu Xie
//
// module: OK_SPI_test_top
//
// Description:
// STEP 1 of the entire chip 4 test, simply an SPI interface test.
// This is a simple test top module to test the SPI interface with the OK host interface.
// It integrates the SPI master module, the clock divider and the ok host interface.
//
// 0x00 WireIn:
//    [7:0] data_in: data to be sent to the SPI slave
//    [15:8] addr: address to be sent to the SPI slave
//    [16]: rstn_ok: reset signal for the SPI master
// 0x20 WireOut:
//    [7:0] data_out: data received from the SPI slave
//    [8]: done: indicates that the SPI transaction is done
// 0x40 TriggerIn:
//    [0]: send_SPI: trigger to start the SPI transaction
//////////////////////////////////////////////////////////////////////////////////

module OK_SPI_test_top(
    input  wire [4:0]   okUH,
    output wire [2:0]   okHU,
    inout  wire [31:0]  okUHU,
    inout  wire         okAA,

    input  wire         sys_clkp,
    input  wire         sys_clkn,

    // wires between the SPI master and the chip
    output wire         SCK,
    output wire         MOSI,
    input  wire         MISO,
    output wire         nCS

    );

    // Clock solution
    wire sys_clk; // 200 MHZ CLOCK WITH PERIOD OF 5 ns
    IBUFGDS osc_clk(.O(sys_clk), .I(sys_clkp), .IB(sys_clkn));

    // OK host interface
    wire rstn_ok;

    // Clock divider to generate 20 mhz clock for SPI master
    wire clk_20m;
    clk_div_sys_20mhz clk_div_inst (
        .sys_clk(sys_clk),
        .rst_n(rstn_ok),
        .clk_out(clk_20m)
    );


    // SPI master instnatiation
    wire send_SPI;
    wire [7:0] addr;
    wire [7:0] data_in;
    wire [7:0] data_out;
    wire done;

    SPI_test_master #(
        .HALF_PERIOD(10) // 5 MHz SCK frequency
    ) spi_master_inst (
        .clk(clk_20m),
        .rst_n(rstn_ok),
        .send_SPI(send_SPI),
        .addr(addr),
        .data_in(data_in),
        .data_out(data_out),
        .done(done),
        .spi_clk(SCK),
        .spi_mosi(MOSI),
        .spi_miso(MISO),
        .spi_cs_n(nCS)
    );


    ///////////////////////////////////////////////////
    // OK host interface instantiation
    wire [65*1-1:0]  okEHx;
    wire okClk;
    wire [112:0] okHE;
    wire [64:0]  okEH;

    // OK host interface instantiation
    wire [31:0] ep00WireIn;
    wire [31:0] ep20WireOut;
    wire [31:0] ep40TriggerIn;



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


okWireIn    wi00(.okHE(okHE),                             .ep_addr(8'h00), .ep_dataout(ep00WireIn));
okWireOut   wo20(.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(ep20WireOut));
okTriggerIn ti40(.okHE(okHE),                             .ep_addr(8'h40), .ep_clk(clk_20m), .ep_trigger(ep40TriggerIn));

    // Connect the OK host interface to the SPI master
    assign rstn_ok = ep00WireIn[16];
    assign addr = ep00WireIn[15:8];
    assign data_in = ep00WireIn[7:0];
    assign send_SPI = ep40TriggerIn[0];

    // Connect the SPI master to the OK host interface
    assign ep20WireOut[7:0] = data_out;
    assign ep20WireOut[8] = done;


endmodule
