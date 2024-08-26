
(* use_dsp = "yes" *) module mac_0_stage_unsigned_8_8_16_bit(
    input [7:0] a,
    input [7:0] b,
    input clk,
    output [15:0] out);

    logic [15:0] acc;

    always @(posedge clk) begin 
        acc <= out + (a * b);
    end

    assign out = acc;
    
endmodule