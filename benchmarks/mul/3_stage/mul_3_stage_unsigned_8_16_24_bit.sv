
(* use_dsp = "yes" *) module mul_3_stage_unsigned_8_16_24_bit(
  input [7:0] a, 
  input [15:0] b, 
  input clk,
  output [23:0] out);

  logic [23:0] stage0;
  logic [23:0] stage1;
  logic [23:0] stage2;

  always @(posedge clk) begin 
    stage0 <= a * b;
    stage1 <= stage0;
    stage2 <= stage1;
  end

  assign out = stage2;
  
endmodule