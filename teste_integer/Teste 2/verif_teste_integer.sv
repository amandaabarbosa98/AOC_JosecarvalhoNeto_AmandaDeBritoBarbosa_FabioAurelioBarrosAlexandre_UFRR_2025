module verify_teste_integer (
    input [3:0] val_in,
    output [4:0] val_out
);

    teste_integer dut (
        .val_in(val_in),
        .val_out(val_out)
    );

    always @(*) begin
        assume (val_in <= 15);
        assert (val_out == val_in + 10);
        assert (val_out <= 31);
    end
endmodule