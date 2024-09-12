
(* use_dsp = "yes" *) module mul_0_stage_unsigned_32_64_96_bit(
  input [31:0] a, 
  input [63:0] b, 
  output [95:0] out);

  assign out = a * b;
  
endmodule