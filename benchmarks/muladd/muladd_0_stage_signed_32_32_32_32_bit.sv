

(* use_dsp = "yes" *) module muladd_0_stage_signed_32_32_32_32_bit (
	input signed [31:0] a,
	input signed [31:0] b,
	input signed [31:0] c,
	output [31:0] out,
	input clk);

	assign out = (a * b) + c;
endmodule