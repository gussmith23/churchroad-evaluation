
(* use_dsp = "yes" *) module mul_0_stage_unsigned_64_64_64_bit (
    input [63:0] a,
    input [63:0] b,
    output [63:0] out);

  assign out = a * b;
  
endmodule