library ieee;
use ieee.std_logic_1164.all;

entity teste_array is
    port (
        addr     : in  integer range 0 to 3;
        data_out : out std_logic_vector(7 downto 0)
    );
    -- TAGS DE VERIFICAÇÃO:
    -- Restringe endereço a 2 bits (0 a 3)
    -- @c2vhdl:ASSUME addr <= 3;
    
    -- Verifica o conteúdo da ROM (usando sintaxe Verilog para os valores hex)
    -- Se endereço é 0, dado deve ser 0x0A (10)
    -- @c2vhdl:ASSERT (addr == 0) ? (data_out == 8'h0A) : 1;
    -- Se endereço é 1, dado deve ser 0xF0 (240)
    -- @c2vhdl:ASSERT (addr == 1) ? (data_out == 8'hF0) : 1;
end teste_array;

architecture behavioral of teste_array is
    type memoria_t is array (0 to 3) of std_logic_vector(7 downto 0);
    signal minha_rom : memoria_t := (
        "00001010", 
        "11110000", 
        "10101010", 
        "01010101"  
    );
begin
    data_out <= minha_rom(addr);
end behavioral;