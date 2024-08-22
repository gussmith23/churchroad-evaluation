module mul_16_32_32(input [15:0] a, input [31:0] b, output [31:0] out);
  assign out = a * b;
endmodule