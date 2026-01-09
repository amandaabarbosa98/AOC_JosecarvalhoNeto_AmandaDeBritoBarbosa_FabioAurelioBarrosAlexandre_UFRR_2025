library ieee;
use ieee.std_logic_1164.all;

entity teste_downto is
    port (
        input_bus : in  std_logic_vector(7 downto 0);
        output_bus: out std_logic_vector(0 to 7) --forçar erro
    ); 
end teste_downto; 

architecture behavioral of teste_downto is
begin
    output_bus <= input_bus;
end behavioral;
