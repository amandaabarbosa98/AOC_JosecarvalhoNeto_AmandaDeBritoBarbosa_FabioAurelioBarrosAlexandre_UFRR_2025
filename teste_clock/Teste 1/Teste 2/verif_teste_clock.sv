module verify_teste_clock (
    input clk,
    input reset,
    output [7:0] count
);

    teste_clock dut (
        .clk(clk),
        .reset(reset),
        .count(count)
    );

    always @(*) begin
    end

    always @(posedge clk) begin
        assert ($past(reset) ? (count == 0) : 1);
        assert (!$past(reset) ? (count == $past(count) + 8'd1) : 1);
    end
endmodule