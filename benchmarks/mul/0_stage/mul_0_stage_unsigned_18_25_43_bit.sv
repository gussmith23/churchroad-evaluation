
(* use_dsp = "yes" *) module mul_0_stage_unsigned_18_25_43_bit(
  input [17:0] a, 
  input [24:0] b, 
  output [42:0] out);

  assign out = a * b;
  
endmodule