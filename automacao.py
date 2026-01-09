import re
import math
import os
import subprocess
import sys

def parse_vhdl(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    info = {
        "entity_name": "",
        "ports": [],
        "assumes": [],
        "asserts": [],
        "has_clock": False,
        "clock_port": ""
    }

    # 1. Entity
    entity_match = re.search(r'entity\s+(\w+)\s+is', content, re.IGNORECASE)
    if entity_match:
        info["entity_name"] = entity_match.group(1)

    # 2. Portas
    port_regex = re.compile(r'^\s*(\w+)\s*:\s*(in|out)\s+([\w\s\(\)]+);', re.MULTILINE | re.IGNORECASE)
    for match in port_regex.finditer(content):
        name = match.group(1)
        direction = match.group(2).lower()
        tipo_bruto = match.group(3).lower()
        
        width = 1
        msb = 0
        
        if "integer" in tipo_bruto:
            range_match = re.search(r'range\s+(\d+)\s+to\s+(\d+)', tipo_bruto)
            if range_match:
                end = int(range_match.group(2))
                width = math.ceil(math.log2(end + 1))
                if width == 0: width = 1
                msb = width - 1
            else:
                width = 32
                msb = 31
        elif "vector" in tipo_bruto:
            vec_match = re.search(r'\((\d+)\s+(downto|to)\s+(\d+)\)', tipo_bruto)
            if vec_match:
                n1 = int(vec_match.group(1))
                n2 = int(vec_match.group(3))
                width = abs(n1 - n2) + 1
                msb = width - 1
        
        if direction == "in" and width == 1 and ("clk" in name or "clock" in name):
            info["has_clock"] = True
            info["clock_port"] = name

        info["ports"].append({
            "name": name,
            "dir": "input" if direction == "in" else "output",
            "width": width,
            "msb": msb
        })

    # 3. Tags
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if "-- @c2vhdl:" in line:
            parts = line.split("@c2vhdl:", 1)[1].strip().split(" ", 1)
            tag_type = parts[0].upper()
            rule = parts[1].strip()
            if rule.endswith(";"): rule = rule[:-1]
            
            if tag_type == "ASSUME":
                info["assumes"].append(rule)
            elif tag_type == "ASSERT":
                info["asserts"].append(rule)

    return info

def generate_verification_wrapper(info, output_path):
    lines = []
    wrapper_name = f"verify_{info['entity_name']}"
    
    lines.append(f"module {wrapper_name} (")
    port_strs = []
    for p in info["ports"]:
        if p["width"] == 1:
            port_strs.append(f"    {p['dir']} {p['name']}")
        else:
            port_strs.append(f"    {p['dir']} [{p['msb']}:0] {p['name']}")
    lines.append(",\n".join(port_strs))
    lines.append(");")
    lines.append("")

    lines.append(f"    {info['entity_name']} dut (")
    conns = [f"        .{p['name']}({p['name']})" for p in info["ports"]]
    lines.append(",\n".join(conns))
    lines.append("    );")
    lines.append("")

    combinational_asserts = []
    sequential_asserts = []
    for rule in info["asserts"]:
        if "$past" in rule:
            sequential_asserts.append(rule)
        else:
            combinational_asserts.append(rule)

    lines.append("    always @(*) begin")
    for rule in info["assumes"]:
        lines.append(f"        assume ({rule});")
    for rule in combinational_asserts:
        lines.append(f"        assert ({rule});")
    lines.append("    end")
    
    if info["has_clock"] and info["clock_port"]:
        lines.append("")
        lines.append(f"    always @(posedge {info['clock_port']}) begin")
        for rule in sequential_asserts:
            lines.append(f"        assert ({rule});")
        lines.append("    end")
    
    lines.append("endmodule")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    return wrapper_name

def generate_sby_config(vhdl_filename, sv_filename, wrapper_module, sby_path, info):
    entity_name = info["entity_name"]
    
    if info["has_clock"]:
        mode_block = "mode bmc\ndepth 20"
    else:
        mode_block = "mode prove"

    config = f"""[options]
{mode_block}

[engines]
smtbmc

[script]
plugin -i ghdl
read_verilog -sv {sv_filename}
ghdl --std=08 {vhdl_filename} -e {entity_name}
prep -top {wrapper_module}
write_verilog -noattr traducao_{entity_name}.v

[files]
{sv_filename}
{vhdl_filename}
"""
    with open(sby_path, "w") as f:
        f.write(config)

def main():
    print("- -Buscando arquivos .vhd - -")
    
    targets = []
    root_dir = "." 

    # 1. Procura na raiz
    try:
        for file in os.listdir(root_dir):
            if file.endswith(".vhd"):
                targets.append((root_dir, file))
    except Exception as e:
        print(f"Erro ao ler raiz: {e}")

    # 2. Procura nas pastas imediatas
    try:
        with os.scandir(root_dir) as entries:
            for entry in entries:
                if entry.is_dir():
                    if entry.name.startswith("."): continue
                    try:
                        sub_files = os.listdir(entry.path)
                        for file in sub_files:
                            if file.endswith(".vhd"):
                                targets.append((entry.path, file))
                    except PermissionError:
                        continue
    except Exception as e:
        print(f"Erro ao escanear pastas: {e}")

    if not targets:
        print("Nenhum arquivo .vhd encontrado.")
        return

    print(f"Encontrados {len(targets)} arquivos únicos.")
    print("-" * 60)

    for folder, filename in targets:
        print(f" Processando na pasta: {folder}")
        print(f" Arquivo: {filename}")
        
        vhdl_path = os.path.join(folder, filename)
        
        try:
            # 1. Análise
            info = parse_vhdl(vhdl_path)
            
            if not info["entity_name"]:
                print("  Entidade não detectada. Pulando.")
                continue

            sv_filename = f"verif_{info['entity_name']}.sv"
            sby_filename = f"{info['entity_name']}.sby"
            
            sv_path = os.path.join(folder, sv_filename)
            sby_path = os.path.join(folder, sby_filename)

            # 2. Gerar arquivos
            wrapper_name = generate_verification_wrapper(info, sv_path)
            generate_sby_config(filename, sv_filename, wrapper_name, sby_path, info)

            # 3. Executar SymbiYosys
            print("    Executando SBY (Logs abaixo)")
            print("   " + "-"*40) 
            
            # Executa e captura a saída
            result = subprocess.run(
                ["sby", "-f", sby_filename], 
                cwd=folder, 
                capture_output=True, 
                text=True
            )
            
            # Imprime todo o log
            print(result.stdout)
            print("   " + "-"*40) 

            # 4. Relatório Final
            output_log = result.stdout
            
            if result.returncode == 0:
                print(f"    [PASS]: Verificação passou com sucesso.")
            else:
                # Procura por falha lógica no texto todo
                if "FAIL" in output_log or "failure" in output_log.lower() or "counterexample" in output_log.lower():
                    print(f"    [FAIL]: Erro de lógica encontrado (Contraexemplo gerado).")
                    
                    # Tenta mostrar onde o rastro foi salvo
                    trace_match = re.search(r'Writing trace to ([^\s]+)', output_log)
                    if trace_match:
                        print(f"      Rastro salvo em: {trace_match.group(1)}")
                else:
                    print(f"    ERRO: Falha na ferramenta ou sintaxe (Verifique o log).\n")

        except Exception as e:
            print(f"    Erro crítico: {e}")
        
        print("=" * 80)
        print("\n")

if __name__ == "__main__":
    main()