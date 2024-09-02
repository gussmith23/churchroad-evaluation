
(* use_dsp = "yes" *) module mac_0_stage_unsigned_16_16_32_bit(
    input [15:0] a,
    input [15:0] b,
    input clk,
    output [31:0] out);

    logic [31:0] acc;

    always @(posedge clk) begin 
        acc <= out + (a * b);
    end

    assign out = acc;
    
endmodule