# TASK 04 — Pipeline + Front-end (Dashboard) + Objective 5 (Common AST)

Este diretório contém uma implementação reprodutível para a **TASK 04**:
- automação de pipeline (detecção VHDL → specs → opcionalmente VHD2VL/Yosys/SymbiYosys/V2C/ESBMC)
- geração de **arquivo auxiliar** (`specs/*.json`) com IO + propriedades (`@c2vhdl:ASSUME/@c2vhdl:ASSERT`)
- **front-end** (dashboard) que lê `results/summary.json`
- **Objective 5**: *front-end unificador* que gera um **AST comum** (schema `aoc-task04-common-ast-v1`)

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
