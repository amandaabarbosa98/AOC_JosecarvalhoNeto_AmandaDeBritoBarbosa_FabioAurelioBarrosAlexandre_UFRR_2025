library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity teste_clock is
    port (
        clk   : in  std_logic;
        reset : in  std_logic;
        count : out std_logic_vector(7 downto 0)
    );
    -- TAGS DE VERIFICAÇÃO (Requer suporte a SystemVerilog Assertions):
    
    -- Se o reset estava ativo no ciclo passado, count atual deve ser 0
    -- @c2vhdl:ASSERT $past(reset) ? (count == 0) : 1;
    
    -- Se reset NÃO estava ativo, count deve ser anterior + 1
    -- @c2vhdl:ASSERT !$past(reset) ? (count == $past(count) + 8'd1) : 1;
    
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