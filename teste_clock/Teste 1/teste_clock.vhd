library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity teste_clock is
    port (
        clk   : in  std_logic;
        reset : in  std_logic;
        count : out std_logic_vector(7 downto 0)
    );
end teste_clock;

architecture behavioral of teste_clock is
    signal reg_count : unsigned(7 downto 0) := (others => '0');
begin
    process(clk, reset)
    begin
        if reset = '1' then
            reg_count <= (others => '0');
        elsif rising_edge(clk) then
            reg_count <= reg_count + 1;
        end if;
    end process;
    
    count <= std_logic_vector(reg_count);
end behavioral;
