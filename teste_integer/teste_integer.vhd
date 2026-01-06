library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity teste_integer is
    port (
        val_in  : in  integer range 0 to 15;
        val_out : out integer range 0 to 31
    );
end teste_integer;

architecture behavioral of teste_integer is
begin
    process(val_in)
    begin
        -- Operação simples para testar propagação de limites
        val_out <= val_in + 10; 
    end process;
end behavioral;