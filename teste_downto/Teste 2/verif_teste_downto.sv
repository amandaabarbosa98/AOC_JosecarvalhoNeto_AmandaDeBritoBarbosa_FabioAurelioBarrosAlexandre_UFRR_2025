module verify_teste_downto (
    input [7:0] input_bus,
    output [7:0] output_bus
);

    teste_downto dut (
        .input_bus(input_bus),
        .output_bus(output_bus)
    );

    always @(*) begin
        assert (input_bus == output_bus);
    end
endmodule