
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 02.10.2026 15:51:22
// Design Name:
// Module Name: LVDS_training_fsm
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


`timescale 1ps/1fs
//-----------------------------------------------------------------------------
// PLACEHOLDER for LVDS_training_fsm - lets the front end simulate before the
// real FSM exists. It loads a fixed IDELAY tap once, never bitslips, and never
// asserts LINK_UP. Replace with the real FSM (same port list).
//-----------------------------------------------------------------------------
module LVDS_training_fsm #(
    parameter [4:0] INIT_TAP = 5'd16
)(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       delay_rdy,
    input  wire [4:0] CNTVALUEOUT,
    input  wire       mmcm_locked,
    output reg  [4:0] CNTVALUEIN,
    output reg        INC,
    output reg        CE,
    output reg        LD,
    output reg        BITSLIP,
    //output wire       CE1_SERDES,
    output reg       LINK_UP,
    input  wire [7:0] data_from_ISERDES
);

    reg [1:0] rdy_sync;   // delay_rdy comes from the refclk domain
    reg       loaded;

    // registers

    reg [3:0]       WAIT_CNT;
    reg             DELAY_DONE; // internal indicator that the tap sweep is finished
    reg [3:0]       WORD_CNT;   // number of words collected during tap sweep
    reg [7:0]      temp_word;  // temporary save the words from ISERDES

    reg [5:0]       TAPSWP_CNT;// number of sweep we have done

    reg             WRD_VLD;   // singal to another evaluation module to check words consistency
    wire            EVA_FIN;   // signal from a sub machine for tap results evaluation.
    reg             DAT_snap;
    reg [7:0]       DAT_snapshot;
    // state machine definition

    reg [3:0] curr_state, next_state;

    localparam                 RST      = 0;
    localparam                 APL_TAP  = 1;
    localparam                 WAIT     = 2;
    localparam                 COLDATA0 = 3;
    localparam                 COLDATA1 = 4;
    localparam                 EVATAP   = 5;
    localparam                 CTREYE   = 6;
    localparam                 PATBC1   = 7;
    localparam                 PAT4D1   = 8;
    localparam                 PATBC2   = 9;
    localparam                 PAT4D2   = 10;
    localparam                 BITSLIP_ST  = 11;
    localparam                 DONE     = 12;


    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rdy_sync   <= 2'b00;
            //loaded     <= 1'b0;
            //CNTVALUEIN <= 5'd0;
            //LD         <= 1'b0;
        end else begin
            rdy_sync <= {rdy_sync[0], delay_rdy};
            //LD       <= 1'b0;
            //if (!loaded && rdy_sync[1] && mmcm_locked) begin
            //    CNTVALUEIN <= INIT_TAP;
            //    LD         <= 1'b1;   // one-cycle load pulse
            //    loaded     <= 1'b1;
            // end
        end
    end
/*
    assign INC        = 1'b0;
    assign CE         = 1'b0;
    assign BITSLIP    = 1'b0;
    assign CE1_SERDES = 1'b1;
    assign LINK_UP    = 1'b0;
*/

wire last_word, last_tapswp;
wire [4:0] recom_tap_value;
wire EYE_VLD;

assign last_word = (WORD_CNT == 4'd7);
assign last_tapswp = (TAPSWP_CNT == 6'd32);

WRD_CON_EVAL  tap_eva_inst (
    .clk(clk),
    .rst_n(rst_n),
    .WRD_COL({temp_word, data_from_ISERDES}), // the words collected during the tap sweep
    .WRD_VLD(WRD_VLD), // the signal to indicate that the words are valid
    .WORD_CNT(WORD_CNT[2:0]),  // number of word cnt
    .last_wrd(last_word), // the signal to indicate that this is the last word of the 8 words collected, this basically means WRD_CNT == 7
    .last_tapswp(last_tapswp), // the signal to indicate that this is the last tap sweep, this basically means TAPSWP_CNT == 32
    .curr_TAP_VALUE(CNTVALUEOUT), // the current tap value

    .EVA_FIN(EVA_FIN), // the signal to indicate that the evaluation is finished
    .EYE_VALID(EYE_VLD), // the signal to indicate that a useable eye has been found,
    .EVA_RESULT(recom_tap_value) // the result of the evaluation


);

// a simple data snapshot of the data from always
always @(posedge clk or negedge rst_n)
begin
    if(!rst_n) begin
        DAT_snapshot <= 0;
    end
    else if (DAT_snap) begin
        DAT_snapshot <=  data_from_ISERDES;
    end
end



// current state reg
always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        curr_state <= RST;
    end
    else begin
        curr_state <= next_state;
    end

end



// registers update

always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        loaded <= 1'b0;
        CNTVALUEIN  <= 5'b0;
        WAIT_CNT    <= 4'd0;
        DELAY_DONE  <= 0;
        LINK_UP     <= 0;
        TAPSWP_CNT  <= 6'd0;
        WORD_CNT    <= 0;
        DAT_snap    <= 0;
    end
    else begin

    case (curr_state)

    RST: begin
     if (rdy_sync[1] && mmcm_locked)
        begin
            CNTVALUEIN <= INIT_TAP;
        end
    end

    APL_TAP: begin
        if(TAPSWP_CNT <= 6'd31)
        begin
            TAPSWP_CNT <=  TAPSWP_CNT+1;
        end
        else begin
            TAPSWP_CNT <=  6'd0;
        end

        if(!loaded)
        begin
            loaded <= 1'b1;
        end
    end

    WAIT: begin
        if(WAIT_CNT < 4'd7)
        begin
            WAIT_CNT <= WAIT_CNT +1;
        end
        else
        begin
            WAIT_CNT <= 0;
        end

    end

    COLDATA0: begin
        temp_word[7:0] <= data_from_ISERDES;
    end

    COLDATA1: begin
        if (WORD_CNT >= 4'd7)
        begin
            WORD_CNT <= 4'd0;
        end
        else
        begin
            WORD_CNT <= WORD_CNT +1;
        end
    end

    EVATAP: begin
        if(TAPSWP_CNT >= 6'd32 && EYE_VLD)
        begin
            TAPSWP_CNT <= 6'd0;
            DELAY_DONE <= 1;
            CNTVALUEIN <= recom_tap_value;
            DAT_snap   <= 1;
        end
    end

    CTREYE: begin

    end

    PATBC1: begin

    end

    PAT4D1: begin

    end

    PATBC2: begin

    end

    PAT4D2: begin

    end

    BITSLIP_ST: begin

    end

    DONE: begin
    LINK_UP <= 1'b1;
    end

    default: begin

    end

    endcase


    end

end


// next state logic update

always @(*)
begin
    // by default these will be the default values
    next_state = curr_state;
    LD = 0;
    CE = 0;
    INC = 0;
    WRD_VLD = 0;
    BITSLIP = 0;
    case(curr_state)

    RST: begin
        if (rdy_sync[1] && mmcm_locked)
        begin
            next_state = APL_TAP;
        end
    end

    APL_TAP: begin
        next_state = WAIT;
        if(!loaded)
        begin
            LD = 1;
        end
        else begin
            CE  = 1;
            INC = 1;
        end
    end

    WAIT: begin
        if(WAIT_CNT >= 4'd7) // waited 8 cycles then jump
        begin
            if(DELAY_DONE) // delay tap has been applied, now it is bitslitp phase
            begin
                next_state = PATBC1;
            end
            else begin
                next_state = COLDATA0;
            end
        end
    end

    COLDATA0: begin
        next_state = COLDATA1;
    end

    COLDATA1: begin
        WRD_VLD = 1'b1;     // the collected word is valid now;
        if (WORD_CNT >= 4'd7)
        begin
            next_state = EVATAP;  // we have collected 8 words
        end
        else begin
            next_state = COLDATA0; // not enough words collected
        end
    end

    EVATAP: begin
        if(EVA_FIN)        // current evaluation finished
        begin
            if(EYE_VLD)            // all the taps are swept
            begin
                next_state = CTREYE;
            end
            else begin
                next_state = APL_TAP;
            end
        end
    end

    CTREYE: begin
    // the state to apply the final tap to centre around the eye
    LD = 1;
    next_state = WAIT;
    end

    PATBC1: begin
    // looking for word BC/4D
    if(DAT_snapshot == 8'hBC)
        next_state = PAT4D1;
    else if (DAT_snapshot == 8'h4D)
        next_state = PAT4D2;
    else // did not get anything, we need to operate bitslip
        next_state = BITSLIP_ST;
    end

    PAT4D1: begin
    // we have found BC, now we need to look for another word 4D
    if(DAT_snapshot == 8'h4D)
        next_state = PATBC2;
    else
        next_state = BITSLIP_ST;
    end

    PATBC2: begin
    // we have already had a BC4D or a 4D.
    if(DAT_snapshot == 8'hBC)
        next_state = PAT4D2;
    else
        next_state = BITSLIP_ST;
    end

    PAT4D2: begin
    // last 4D to go so we should have at least had 4D,BC. or BC4D, BC.
    if(DAT_snapshot == 8'h4D)
        next_state = DONE;
    else
        next_state = BITSLIP_ST;

    end

    BITSLIP_ST: begin
    // apply one cycle of bitslip
    BITSLIP = 1'b1;
    next_state  =   WAIT;
    end

    DONE: begin

    end

    default: begin

    end

    endcase


end

endmodule