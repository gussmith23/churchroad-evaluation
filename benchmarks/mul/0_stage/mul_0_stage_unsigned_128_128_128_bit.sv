
(* use_dsp = "yes" *) module mul_0_stage_unsigned_128_128_128_bit (
    input [127:0] a,
    input [127:0] b,
    output [127:0] out);

  assign out = a * b;
  
endmodule