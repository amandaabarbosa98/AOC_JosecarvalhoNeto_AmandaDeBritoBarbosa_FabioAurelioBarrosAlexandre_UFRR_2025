library ieee;
use ieee.std_logic_1164.all;

entity teste_array is
    port (
        addr     : in  integer range 0 to 3;
        data_out : out std_logic_vector(7 downto 0)
    );
end teste_array;

architecture behavioral of teste_array is
    -- Definindo um tipo array de 4 posições, cada uma com 8 bits
    type memoria_t is array (0 to 3) of std_logic_vector(7 downto 0);
    signal minha_rom : memoria_t := (
        "00001010", -- Índice 0
        "11110000", -- Índice 1
        "10101010", -- Índice 2
        "01010101"  -- Índice 3
    );
begin
    data_out <= minha_rom(addr);
end behavioral;
