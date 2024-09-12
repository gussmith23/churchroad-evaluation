
(* use_dsp = "yes" *) module mac_0_stage_unsigned_32_32_64_bit(
    input [31:0] a,
    input [31:0] b,
    input clk,
    output [63:0] out);

    logic [63:0] acc;

    always @(posedge clk) begin 
        acc <= out + (a * b);
    end

    assign out = acc;
    
endmodule