library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity teste_integer is
    port (
        val_in  : in  integer range 0 to 15;
        val_out : out integer range 0 to 31
    );
    -- TAGS DE VERIFICAÇÃO PARA O SCRIPT PYTHON:
    -- O range de entrada é 0-15 (4 bits), restringimos a busca a isso:
    -- @c2vhdl:ASSUME val_in <= 15;
    
    -- A saída deve ser a entrada + 10:
    -- @c2vhdl:ASSERT val_out == val_in + 10;
    
    -- A saída não deve estourar 31:
    -- @c2vhdl:ASSERT val_out <= 31;
end teste_integer;

architecture behavioral of teste_integer is
begin
    process(val_in)
    begin
        val_out <= val_in + 10;
    end process;
end behavioral;