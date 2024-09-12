
module muladd_unsigned_0stage_16_16_32_32(
  input [15:0] a, 
  input [15:0] b, 
  input [31:0] c, 
  output [31:0] out);

  assign out = c + a * b;
  
endmodule