
(* use_dsp = "yes" *) module mul_1_stage_unsigned_8_16_24_bit(
  input [7:0] a, 
  input [15:0] b, 
  input clk,
  output [23:0] out);

  logic unsigned [23:0] stage0;

  always @(posedge clk) begin 
    stage0 <= a * b;
  end

  assign out = stage0;
  
endmodule