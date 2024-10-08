
(* use_dsp = "yes" *) module muladd_2_stage_signed_8_8_8_8_bit (
	input signed [7:0] a,
	input signed [7:0] b,
	input signed [7:0] c,
	output [7:0] out,
	input clk);

    logic signed [7:0] stage0;
    logic signed [7:0] stage1;

    always @(posedge clk) begin 
        stage0 <= (a * b) + c;
        stage1 <= stage0;
    end

	assign out = stage1;

endmodule