
(* use_dsp = "yes" *) module mul_0_stage_unsigned_8_8_16_bit(
  input [7:0] a, 
  input [7:0] b, 
  output [15:0] out);

  assign out = a * b;
  
endmodule