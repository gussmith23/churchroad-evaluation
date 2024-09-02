
(* use_dsp = "yes" *) module mul_0_stage_unsigned_32_48_80_bit(
  input [31:0] a, 
  input [47:0] b, 
  output [79:0] out);

  assign out = a * b;
  
endmodule