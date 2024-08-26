
(* use_dsp = "yes" *) module mul_0_stage_unsigned_18_18_36_bit(
  input [17:0] a, 
  input [17:0] b, 
  output [35:0] out);

  assign out = a * b;
  
endmodule