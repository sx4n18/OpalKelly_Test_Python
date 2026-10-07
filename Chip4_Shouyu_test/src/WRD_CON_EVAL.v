`timescale 1ps/1fs

//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 10/07/2026 01:39:05 PM
// Design Name:
// Module Name: WRD_CON_EVAL
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


/////////////////////////////////////////////////////////////////////////////////
// a simple module to evaluate the words collected during the tap sweep,
// and decide if the link is up or not

module WRD_CON_EVAL(
    input  wire         clk,
    input  wire         rst_n,
    input  wire [15:0]  WRD_COL, // the words collected during the tap sweep
    input  wire         WRD_VLD, // the signal to indicate that the words are valid
    input  wire [2:0]   WORD_CNT,  // number of word cnt
    input  wire         last_wrd, // the signal to indicate that this is the last word of the 8 words collected, this basically means WRD_CNT == 7
    input  wire         last_tapswp, // the signal to indicate that this is the last tap sweep, this basically means TAPSWP_CNT == 32
    input  wire [4:0]   curr_TAP_VALUE, // the current tap value

    output reg          EVA_FIN, // the signal to indicate that the evaluation is finished
    output reg          EYE_VALID, // the signal to indicate that a useable eye has been found,
    output reg  [4:0]   EVA_RESULT // the result of the evaluation
    );


    // memory to store the words collected during the tap sweep
    reg [15:0] WRD_MEM [0:7]; // 8 words, each 16 bits wide
    reg [31:0]  EVA_RESULT_REG; // temporary storage for the evaluation result, 1 hot evaluation for 32 taps, each bit indicates if the words are consistent or not for that tap value
    reg EVA_CALC_PENDING; // signal to indicate that the final evaluation should start

    // evaluation function to return a simple 1/0 to indicate if the words are consistent or not
    // The function will tke 8 words and check if they are all the same, if they are, return 1, else return 0
    function [0:0] check_words_consistency;
        input [15:0] word0;
        input [15:0] word1;
        input [15:0] word2;
        input [15:0] word3;
        input [15:0] word4;
        input [15:0] word5;
        input [15:0] word6;
        input [15:0] word7;
        begin
            if (word0 == word1 && word1 == word2 && word2 == word3 && word3 == word4 && word4 == word5 && word5 == word6 && word6 == word7) begin
                check_words_consistency = 1'b1;
            end else begin
                check_words_consistency = 1'b0;
            end
        end
    endfunction

    // function to produce a recommneded tap value based on the evaluation result, this function will take the 32 bit evaluation result and return the recommended tap value
    // this will only be called when all 32 taps have been evaluated, and we should start the tap value from 0 for simplicity.
    // the function aims to find the longest consecutive 1's in the eva_result, and return the middle tap value of that range as the recommended tap value.
    function [4:0] recommend_tap_value;
        input [31:0] eva_result;
        integer i;
        integer start_idx;
        integer max_start_idx;
        integer max_end_idx;
        integer end_idx;
        integer max_len;
        integer curr_len;
        begin
            start_idx = -1;
            end_idx = -1;
            max_len = 0;
            curr_len = 0;
            for (i = 0; i < 32; i = i + 1) begin
                if (eva_result[i] == 1'b1) begin // if current bit is 1, we are in a consecutive 1's range
                    if (start_idx == -1) begin   // if this is the first 1 in the range, record the start index
                        start_idx = i;
                    end
                    curr_len = curr_len + 1;
                end else begin                  // if current bit is 0, we are out of the consecutive 1's range
                   if (curr_len > max_len) begin
                    max_len       = curr_len;
                    max_start_idx = start_idx;
                    max_end_idx   = i - 1;
                    end
                    start_idx = -1;          // reset the start index for the next range
                    curr_len = 0;
                end
            end
            // check at the end of the loop
            if (curr_len > max_len) begin   // if we are still not out of the range by the end of the loop, we need to check if the current length is greater than the max length
                max_len = curr_len;
                max_end_idx = 31;
                max_start_idx = start_idx;
            end
            if (max_len > 0) begin
                recommend_tap_value = (max_start_idx + max_end_idx) / 2; // return the middle tap value of the longest consecutive 1's range
            end else begin
                recommend_tap_value = 5'd0; // if no consecutive 1's found, return 0 as the recommended tap value
            end
        end
    endfunction


    // assign the 8 words to the function inputs
    wire words_consistent;
    assign words_consistent = check_words_consistency(WRD_MEM[0], WRD_MEM[1], WRD_MEM[2], WRD_MEM[3], WRD_MEM[4], WRD_MEM[5], WRD_MEM[6], WRD_COL);

    // store the words in the memory
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            EVA_FIN <= 1'b0;
            EVA_RESULT <= 5'd0;
            EVA_CALC_PENDING <= 1'b0;
            EYE_VALID <= 1'b0;
        end else if (WRD_VLD) begin
            WRD_MEM[WORD_CNT] <= WRD_COL; // store the collected word in the memory
            if (last_wrd) begin // if we have collected 7 words, and we are now collecting the 8th word, we can evaluate the words
                EVA_RESULT_REG[curr_TAP_VALUE] <= words_consistent; // store the evaluation result in the register
                if (last_tapswp) begin // if we are currently at 32 tap sweeps, we can finish the evaluation
                    EVA_CALC_PENDING <= 1'b1;
                end
                else begin   // if we are not at 32 tap sweeps, we can continue to the next tap sweep
                    EVA_CALC_PENDING <= 1'b0;
                    EVA_FIN         <= 1'b1;
                end
            end
        end
        else if (EVA_CALC_PENDING) begin
            EVA_RESULT <= recommend_tap_value(EVA_RESULT_REG); // get the recommended tap value based on the evaluation result
            EYE_VALID  <= (EVA_RESULT_REG != 32'd0); // if the evaluation result is not all 0's, then we have a valid eye
            EVA_FIN <= 1'b1; // indicate that the evaluation is finished
        end
        else begin
            EVA_FIN <= 1'b0; // reset the evaluation finished signal
            EYE_VALID <= 1'b0; // reset the eye valid signal
        end
    end





endmodule
