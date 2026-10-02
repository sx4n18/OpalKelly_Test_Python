`timescale 1ns / 1ps

/////////////////////////////////////////////////////////////////////////////////////
// This will be a simple interface that encapsulate the necessary logic to handle and train
// the LVDS interface.
// The input ports are:
// 1. clock pair: CLK_P and CLK_N
// 2. data pair: DATA_P and DATA_N
// 3. reset: rst_n
// 4. refclk: refclk on FPGA, used to configure the IDELAYCTRL block
// The output ports are:
// 1. data_out: the output data after training
// 2. data_valid: a signal that indicates when the data_out is valid
// 3. mmcm_locked: a signal that indicates when the MMCM is locked
// 4. TRN_DONE: a signal to send back to chip/host to indicate that the training is done, link is up
/////////////////////////////////////////////////////////////////////////////////////

module LVDS_training_blk(
    input wire CLK_P,
    input wire CLK_N,
    input wire DATA_P,
    input wire DATA_N,
    input wire rst_n,
    input wire refclk,
    output reg [7:0] data_out,
    output reg data_valid,
    output     mmcm_locked,         // the mmcm locked signal, this can be monitored by host to know our FSM's clock is valid now.
    output reg TRN_DONE
);

// internal signals
wire LVDS_clk; //single-ended clock signal after differential to single-ended conversion
wire LVDS_data;
wire delay_rdy; // signal to indicate that the IDELAYCTRL block is ready


// instantite the primitives

// IBUFDS
IBUFDS #(
    .DIFF_TERM("TRUE"), // Differential Termination
    .IBUF_LOW_PWR("FALSE") // Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
) IBUFDS_clk_inst (
    .O(LVDS_clk), // Single-ended output
    .I(CLK_P), // Diff_p input (connect directly to top-level port)
    .IB(CLK_N) // Diff_n input (connect directly to top-level port)
);

IBUFDS #(
    .DIFF_TERM("TRUE"), // Differential Termination
    .IBUF_LOW_PWR("FALSE") // Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
) IBUFDS_data_inst (
    .O(LVDS_data), // Single-ended output
    .I(DATA_P), // Diff_p input (connect directly to top-level port)
    .IB(DATA_N) // Diff_n input (connect directly to top-level port)
);

// MMCM to generate the necessary clock for FSM and IDLEAYE2

wire mmcm_clkfb;
wire clk_300m;
wire clk_75m;

MMCME2_BASE #(
    .CLKIN1_PERIOD    (13.333),
    .DIVCLK_DIVIDE    (1),
    .CLKFBOUT_MULT_F  (8.0),

    .CLKOUT0_DIVIDE_F (2.0),   // 600 / 2 = 300 MHz
    .CLKOUT1_DIVIDE   (8),     // 600 / 8 = 75 MHz

    .CLKOUT0_PHASE    (0.0),
    .CLKOUT1_PHASE    (0.0)
) u_mmcm (
    .CLKIN1   (clk_75m_in),

    .CLKFBOUT (mmcm_clkfb),
    .CLKFBIN  (mmcm_clkfb),

    .CLKOUT0  (clk_300m),
    .CLKOUT1  (clk_75m),

    .LOCKED   (mmcm_locked),

    .RST      (mmcm_rst),
    .PWRDWN   (1'b0)
);


// IDELAYCTRL
IDELAYCTRL IDELAYCTRL_inst (
    .RDY(delay_rdy), // Ready output (not used in this example)
    .REFCLK(refclk), // Reference clock input
    .RST(~rst_n) // Reset input (active high)
);

// IDELAYE2 for data signal
wire [4:0] CNTVALUEOUT;
wire DATAOUT;
// ctrl signals from FSM
wire [4:0] CNTVALUEIN;
wire INC, CE, LD;

IDELAYE2 #(
   .CINVCTRL_SEL("FALSE"),          // Enable dynamic clock inversion (FALSE, TRUE)
   .DELAY_SRC("IDATAIN"),           // Delay input (IDATAIN, DATAIN)
   .HIGH_PERFORMANCE_MODE("FALSE"), // Reduced jitter ("TRUE"), Reduced power ("FALSE")
   .IDELAY_TYPE("VAR_LOAD"),           // FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
   .IDELAY_VALUE(0),                // Input delay tap setting (0-31)
   .PIPE_SEL("FALSE"),              // Select pipelined mode, FALSE, TRUE
   .REFCLK_FREQUENCY(200.0),        // IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
   .SIGNAL_PATTERN("DATA")          // DATA, CLOCK input signal
)
IDELAYE2_DAT (
   .CNTVALUEOUT(CNTVALUEOUT), // 5-bit output: Counter value output
   .DATAOUT(DATAOUT),         // 1-bit output: Delayed data output
   .C(clk_75m),                     // 1-bit input: Clock input
   .CE(CE),                   // 1-bit input: Active high enable increment/decrement input
   .CINVCTRL(1'b0),       // 1-bit input: Dynamic clock inversion input
   .CNTVALUEIN(CNTVALUEIN),   // 5-bit input: Counter value input
   .DATAIN(),           // 1-bit input: Internal delay data input
   .IDATAIN(LVDS_data),         // 1-bit input: Data input from the I/O
   .INC(INC),                 // 1-bit input: Increment / Decrement tap delay input
   .LD(LD),                   // 1-bit input: Load IDELAY_VALUE input
   .LDPIPEEN(1'b0),       // 1-bit input: Enable PIPELINE register to load data input
   .REGRST(~rst_n)            // 1-bit input: Active-high reset tap-delay input
);

// ISERDESE2 for data signal
wire [7:0] Q;
wire BITSLIP;
wire CE1_SERDES;

ISERDESE2 #(
   .DATA_RATE("DDR"),           // DDR, SDR
   .DATA_WIDTH(8),              // Parallel data width (2-8,10,14)
   // INIT_Q1 - INIT_Q4: Initial value on the Q outputs (0/1)
   .INIT_Q1(1'b0),
   .INIT_Q2(1'b0),
   .INIT_Q3(1'b0),
   .INIT_Q4(1'b0),
   .INTERFACE_TYPE("NETWORKING"),   // MEMORY, MEMORY_DDR3, MEMORY_QDR, NETWORKING, OVERSAMPLE
   .IOBDELAY("IFD"),           // NONE, BOTH, IBUF, IFD
   .NUM_CE(1),                  // Number of clock enables (1,2)
   .OFB_USED("FALSE"),          // Select OFB path (FALSE, TRUE)
   .SERDES_MODE("MASTER"),      // MASTER, SLAVE
   // SRVAL_Q1 - SRVAL_Q4: Q output values when SR is used (0/1)
   .SRVAL_Q1(1'b0),
   .SRVAL_Q2(1'b0),
   .SRVAL_Q3(1'b0),
   .SRVAL_Q4(1'b0)
)
ISERDESE2_inst (
   .O(O),                       // 1-bit output: Combinatorial output
   // Q1 - Q8: 1-bit (each) output: Registered data outputs
   .Q1(Q[0]),
   .Q2(Q[1]),
   .Q3(Q[2]),
   .Q4(Q[3]),
   .Q5(Q[4]),
   .Q6(Q[5]),
   .Q7(Q[6]),
   .Q8(Q[7]),
   // SHIFTOUT1, SHIFTOUT2: 1-bit (each) output: Data width expansion output ports
   .SHIFTOUT1(),
   .SHIFTOUT2(),
   .BITSLIP(BITSLIP),           // 1-bit input: The BITSLIP pin performs a Bitslip operation synchronous to
                                // CLKDIV when asserted (active High). Subsequently, the data seen on the Q1
                                // to Q8 output ports will shift, as in a barrel-shifter operation, one
                                // position every time Bitslip is invoked (DDR operation is different from
                                // SDR).
   // CE1, CE2: 1-bit (each) input: Data register clock enable inputs
   .CE1(CE1_SERDES),
   .CE2(),
   .CLKDIVP(),           // 1-bit input: TBD
   // Clocks: 1-bit (each) input: ISERDESE2 clock input ports
   .CLK(clk_300m),                   // 1-bit input: High-speed clock
   .CLKB(),                 // 1-bit input: High-speed secondary clock
   .CLKDIV(clk_75m),             // 1-bit input: Divided clock
   .OCLK(),                 // 1-bit input: High speed output clock used when INTERFACE_TYPE="MEMORY"
   // Dynamic Clock Inversions: 1-bit (each) input: Dynamic clock inversion pins to switch clock polarity
   .DYNCLKDIVSEL(), // 1-bit input: Dynamic CLKDIV inversion
   .DYNCLKSEL(),       // 1-bit input: Dynamic CLK/CLKB inversion
   // Input Data: 1-bit (each) input: ISERDESE2 data input ports
   .D(),                       // 1-bit input: Data input
   .DDLY(LVDS_data),                 // 1-bit input: Serial data from IDELAYE2
   .OFB(),                   // 1-bit input: Data feedback from OSERDESE2
   .OCLKB(),               // 1-bit input: High speed negative edge output clock
   .RST(~rst_n),                   // 1-bit input: Active high asynchronous reset
   // SHIFTIN1, SHIFTIN2: 1-bit (each) input: Data width expansion input ports
   .SHIFTIN1(),
   .SHIFTIN2()
);

// FSM to control the IDELAYE2 and ISERDESE2
LVDS_training_fsm u_LVDS_training_fsm (
    .clk(clk_75m),
    .rst_n(rst_n),
    .delay_rdy(delay_rdy),
    .CNTVALUEOUT(CNTVALUEOUT),
    .mmcm_locked(mmcm_locked),
    .CNTVALUEIN(CNTVALUEIN),
    .INC(INC),
    .CE(CE),
    .LD(LD),
    .BITSLIP(BITSLIP),
    .CE1_SERDES(CE1_SERDES),
    .data_from_ISERDES(Q)
);





endmodule