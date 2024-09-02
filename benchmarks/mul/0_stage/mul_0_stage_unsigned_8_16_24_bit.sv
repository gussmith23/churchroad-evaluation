
(* use_dsp = "yes" *) module mul_0_stage_unsigned_8_16_24_bit(
  input [7:0] a, 
  input [15:0] b, 
  output [23:0] out);

  assign out = a * b;
  
endmodule