# AOC_JosecarvalhoNeto_AmandaDeBritoBarbosa_FabioAurelioBarrosAlexandre_UFRR_2025

Visão geral

Este repositório contém a implementação da TASK 04, com um pipeline automatizado para processar designs em VHDL, extrair propriedades de verificação e gerar artefatos organizados para análise. O foco é tornar o fluxo reproduzível, rastreável e fácil de validar por meio de um resumo consolidado e de um dashboard.

O principal diferencial entregue é a Parte 05 (mais avançado): um Front-end unificador com AST comum, que gera uma representação intermediária padronizada para cada design (Common AST), unificando interface, propriedades e metadados de origem em um único formato (*.ast.json).

O que foi feito (resumo do processo)

Criação dos casos de teste (Objetivo 1)
Foram criados quatro designs de teste cobrindo os constructs exigidos:

teste_downto: vetores com downto e inversão de índices, com @c2vhdl:ASSERT de equivalência.

teste_integer: portas integer range ..., com @c2vhdl:ASSUME e @c2vhdl:ASSERT.

teste_array: ROM usando array, com asserts condicionais por endereço.

teste_clock: processo sequencial com clock/reset (rising_edge(clk)) e propriedades temporais com $past(...).

Automação do pipeline (Objetivo 4)
O script task04/run_task04.py detecta os VHDL, extrai portas e tags @c2vhdl:ASSUME/@c2vhdl:ASSERT, gera um arquivo auxiliar por design em task04/specs/*.json e consolida resultados em:

task04/results/summary.json

task04/results/summary.csv

AST comum (Objetivo 5)
Para cada design é gerado um arquivo task04/results/ast/<design>.ast.json com schema:

aoc-task04-common-ast-v1
Esse Common AST reúne: metadados, interface (ports), propriedades (properties) e estrutura quando disponível (wires/cells/stats).

Dashboard (frontend)
O dashboard (servido por task04/serve_dashboard.py) lê summary.json e mostra o status por etapa e por design, com links para spec.json e ast.json.

Estrutura principal

task04/inputs_vhdl/ — VHDLs de teste com tags @c2vhdl:ASSUME/@c2vhdl:ASSERT

task04/specs/ — arquivos auxiliares gerados (*.json)

task04/results/ — summary.json, summary.csv e ast/*.ast.json

task04/run_task04.py — script principal do pipeline

task04/serve_dashboard.py + task04/dashboard/ — frontend (dashboard)

task04/unify_ast.py + task04/ast_frontend/ — geração/unificação do AST comum

Como executar

Na raiz do repositório:

python3 task04/run_task04.py --in task04/inputs_vhdl --out task04 --run-yosys --gen-ast


Resultados esperados:

task04/specs/*.json

task04/results/summary.json

task04/results/summary.csv

task04/results/ast/*.ast.json

Abrir o dashboard
python3 task04/serve_dashboard.py


Abra no navegador:

http://localhost:8000/task04/dashboard/

Para parar o servidor: Ctrl + C no terminal.

Observação sobre etapas opcionais (SBY/ESBMC)

O dashboard e o summary podem indicar etapas como SKIP/FAIL quando ferramentas não estão instaladas no ambiente (ex.: vhd2vl, sby, etc.). Mesmo nesses casos, o pipeline mantém a geração dos artefatos principais (specs, summary e Common AST) e registra a causa no campo de notas do resumo.
