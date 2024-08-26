
(* use_dsp = "yes" *) module mac_0_stage_unsigned_64_64_128_bit(
    input [63:0] a,
    input [63:0] b,
    input clk,
    output [127:0] out);

    logic [127:0] acc;

    always @(posedge clk) begin 
        acc <= out + (a * b);
    end

    assign out = acc;
    
endmodule