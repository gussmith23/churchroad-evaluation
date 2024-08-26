
(* use_dsp = "yes" *) module mul_0_stage_unsigned_32_32_32_bit (
    input [31:0] a,
    input [31:0] b,
    output [31:0] out);

  assign out = a * b;
  
endmodule