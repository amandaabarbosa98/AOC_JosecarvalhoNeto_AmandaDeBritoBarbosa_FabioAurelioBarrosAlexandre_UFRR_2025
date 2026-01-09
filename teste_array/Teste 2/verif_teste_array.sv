module verify_teste_array (
    input [1:0] addr,
    output [7:0] data_out
);

    teste_array dut (
        .addr(addr),
        .data_out(data_out)
    );

    always @(*) begin
        assume (addr <= 3);
        assert ((addr == 0) ? (data_out == 8'h0A) : 1);
        assert ((addr == 1) ? (data_out == 8'hF0) : 1);
    end
endmodule