# TASK 04 — Pipeline + Front-end (Dashboard) + GHDL/AST

Esse diretório detalha o funcionamento da etapa (04) de *pipeline* com a etapa (05) de GHDL + AST:

- Automação de pipeline (detecção VHDL → specs → opcionalmente VHD2VL/Yosys/SymbiYosys/V2C/ESBMC)
- Geração de **arquivo auxiliar** (`specs/*.json`) com IO + propriedades (`@c2vhdl:ASSUME/@c2vhdl:ASSERT`)
- **Front-end** (dashboard) que lê `results/summary.json`
- **Front-end unificador** que gera um **AST comum** (schema `aoc-task04-common-ast-v1`)

## 1) Executar o pipeline (mínimo)
```bash
python3 task04/run_task04.py --in task04/inputs_vhdl --out task04
```

Gera:
- `task04/specs/*.json`
- `task04/results/summary.json` + `summary.csv`

## 2) Rodar Yosys (gera também Yosys JSON)
Ajuste `task04/tools.json` e execute:
```bash
python3 task04/run_task04.py --in task04/inputs_vhdl --out task04 --run-yosys
```

## 3) Rodar SymbiYosys
```bash
python3 task04/run_task04.py --in task04/inputs_vhdl --out task04 --run-yosys --run-sby
```

Logs em `task04/logs/sby/`.

## 4) Gerar Common AST (Objective 5)
Sem Yosys (VHDL-only):
```bash
python3 task04/run_task04.py --in task04/inputs_vhdl --out task04 --gen-ast
```

Com Yosys (estrutura + propriedades):
```bash
python3 task04/run_task04.py --in task04/inputs_vhdl --out task04 --run-yosys --gen-ast
```

Saída:
- `task04/results/ast/<design>.ast.json`

## 5) Abrir o dashboard
```bash
python3 task04/serve_dashboard.py
```
Abra: `http://localhost:8000/task04/dashboard/`

## 6) Configurar ferramentas
ai agora vc edita `task04/tools.json` com os comandos reais do seu ambiente (WSL2).

---

## Referências

[Como instalar o WSL 2 (Ubuntu) no Windows 11/10 | 2025](https://www.youtube.com/watch?v=O8KmK3vXl28)
[Formal Verification of Verilog HDL with Yosys-SMTBMC (33c3)](https://www.youtube.com/watch?v=VJsMLPGg4U4)
[Getting Started with VHDL on Linux (GHDL & GTKWave)](https://www.youtube.com/watch?v=dvLeDNbXfFw)
[Como compilar VHDL utilizando GHDL - Tutorial (ambiente de código aberto)](https://www.youtube.com/watch?v=SihNA2rcS_0)
[Simulating VDHL code with GHDL](https://www.youtube.com/watch?v=j9hya97kRJA)
[VHDL Tutorial](https://www.youtube.com/playlist?list=PLEdaowO6UzNENeQ2WHyGC6mlmggnnhMD6)
[Very Basic Introduction to Formal Verification](https://www.youtube.com/watch?v=9e7F1XhjhKw)
YosysHQ  
https://symbiyosys.readthedocs.io/en/latest/quickstart.html?utm_source=chatgpt.com
https://yosyshq.readthedocs.io/projects/yosys/en/0.45/appendix/auxprogs.html?utm_source=chatgpt.com
https://gritbub-ghdl.readthedocs.io/en/latest/using/Simulation.html?utm_source=chatgpt.com
