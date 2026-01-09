import re
import math
import os
import subprocess
import sys

def parse_vhdl(filename):
    """
    Lê o arquivo VHDL e extrai:
    1. Nome da Entity
    2. Portas (convertendo integer range para bits)
    3. Tags de verificação (@c2vhdl)
    """
    with open(filename, 'r') as f:
        content = f.read()

    info = {
        "entity_name": "",
        "ports": [],
        "assumes": [],
        "asserts": []
    }

    # 1. Achar nome da Entity
    entity_match = re.search(r'entity\s+(\w+)\s+is', content, re.IGNORECASE)
    if entity_match:
        info["entity_name"] = entity_match.group(1)

    # 2. Achar Portas e converter Range -> Bits
    # Ex: val_in : in integer range 0 to 15;
    port_pattern = re.compile(r'(\w+)\s*:\s*(in|out)\s+integer\s+range\s+(\d+)\s+to\s+(\d+)', re.IGNORECASE)
    
    for match in port_pattern.finditer(content):
        name = match.group(1)
        direction = match.group(2).lower() # 'in' ou 'out'
        # start = int(match.group(3)) # geralmente 0
        end = int(match.group(4))
        
        # Calcula bits necessários: ceil(log2(max + 1))
        # Ex: range 0 to 15 (max 15) -> 4 bits
        width = math.ceil(math.log2(end + 1))
        if width == 0: width = 1 
        
        info["ports"].append({
            "name": name,
            "dir": "input" if direction == "in" else "output",
            "width": width,
            "msb": width - 1
        })

    # 3. Extrair Tags @c2vhdl
    # Procura por linhas -- @c2vhdl:TYPE regra
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if "-- @c2vhdl:" in line:
            # Separa o tipo (ASSERT/ASSUME) do conteúdo
            parts = line.split("@c2vhdl:", 1)[1].strip().split(" ", 1)
            tag_type = parts[0].upper() # ASSUME ou ASSERT
            rule = parts[1].strip()
            
            # Limpeza: remove ponto e vírgula final se existir
            if rule.endswith(";"):
                rule = rule[:-1]
            
            if tag_type == "ASSUME":
                info["assumes"].append(rule)
            elif tag_type == "ASSERT":
                info["asserts"].append(rule)

    return info

def generate_verification_wrapper(info, output_filename):
    """Gera o arquivo SystemVerilog que conecta o DUT e aplica as regras."""
    
    lines = []
    wrapper_name = f"verify_{info['entity_name']}"
    
    lines.append(f"module {wrapper_name} (")
    
    # Declaração das portas do wrapper (iguais as do DUT)
    port_decls = []
    for p in info["ports"]:
        port_decls.append(f"    {p['dir']} [{p['msb']}:0] {p['name']}")
    lines.append(",\n".join(port_decls))
    lines.append(");")
    lines.append("")

    # Instância do DUT (VHDL original)
    lines.append(f"    {info['entity_name']} dut (")
    connections = []
    for p in info["ports"]:
        connections.append(f"        .{p['name']}({p['name']})")
    lines.append(",\n".join(connections))
    lines.append("    );")
    lines.append("")

    # Bloco de Verificação
    lines.append("    always @(*) begin")
    
    # Inserir ASSUMES
    if info["assumes"]:
        lines.append("        // Restrições (Assumes)")
        for rule in info["assumes"]:
            lines.append(f"        assume ({rule});")
            
    lines.append("")
    
    # Inserir ASSERTS
    if info["asserts"]:
        lines.append("        // Verificações (Asserts)")
        for rule in info["asserts"]:
            lines.append(f"        assert ({rule});")
            
    lines.append("    end")
    lines.append("endmodule")

    with open(output_filename, "w") as f:
        f.write("\n".join(lines))
    
    return wrapper_name

def generate_sby_config(vhdl_file, sv_file, wrapper_module, sby_filename):
    """Gera o arquivo .sby de configuração."""
    
    # Extrai o nome da entidade (sem .vhd) para o comando -e
    entity_name = vhdl_file.replace('.vhd', '')

    config = f"""[options]
mode prove

[engines]
smtbmc

[script]
# 1. Carrega o plugin do GHDL (ESSENCIAL PARA LER VHDL)
plugin -i ghdl

# 2. Lê o wrapper em SystemVerilog (instrumentação)
read_verilog -sv {sv_file}

# 3. Usa o GHDL para ler o arquivo VHDL original
# --std=08 garante compatibilidade com VHDL 2008
ghdl --std=08 {vhdl_file} -e {entity_name}

# 4. Prepara o topo (wrapper)
prep -top {wrapper_module}

write_verilog -noattr traducao_final.v

[files]
{sv_file}
{vhdl_file}
"""
    with open(sby_filename, "w") as f:
        f.write(config)

def main():
    vhdl_file = "teste_integer.vhd"
    
    if not os.path.exists(vhdl_file):
        print(f"Erro: Arquivo {vhdl_file} não encontrado.")
        return

    print(f"--- 1. Analisando {vhdl_file} ---")
    info = parse_vhdl(vhdl_file)
    print(f"Entidade: {info['entity_name']}")
    print(f"Portas detectadas: {len(info['ports'])}")
    print(f"Regras extraídas: {len(info['assumes'])} Assumes, {len(info['asserts'])} Asserts")

    # Nome dos arquivos gerados
    sv_file = f"verif_{info['entity_name']}.sv"
    sby_file = f"{info['entity_name']}.sby"

    print(f"--- 2. Gerando Instrumentação ({sv_file}) ---")
    wrapper_name = generate_verification_wrapper(info, sv_file)

    print(f"--- 3. Gerando Configuração SBY ({sby_file}) ---")
    generate_sby_config(vhdl_file, sv_file, wrapper_name, sby_file)

    print(f"--- 4. Executando SymbiYosys ---")
    try:
        # Executa o comando: sby -f nome_do_arquivo.sby
        subprocess.run(["sby", "-f", sby_file], check=True)
    except FileNotFoundError:
        print("ERRO: O comando 'sby' não foi encontrado.")
        print("Certifique-se de que o OSS CAD Suite (SymbiYosys) está instalado e no PATH.")
    except subprocess.CalledProcessError:
        print("A verificação falhou ou encontrou erros (veja o log acima).")

if __name__ == "__main__":
    main()