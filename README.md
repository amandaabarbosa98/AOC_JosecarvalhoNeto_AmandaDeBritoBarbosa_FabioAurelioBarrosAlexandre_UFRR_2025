# AOC_JosecarvalhoNeto_AmandaDeBritoBarbosa_FabioAurelioBarrosAlexandre_UFRR_2025
# Tutorial —  (GitHub → Ubuntu → Execução → Dashboard)

Este guia mostra como acessar o repositório no GitHub, clonar no Ubuntu, executar o pipeline da TASK 04 e abrir o dashboard localmente.

---

## 1) Acessar o GitHub e conferir o repositório

1. Acesse **github.com** e faça login.
2. Entre no repositório:
   - `amandaabarbosa98/AOC_JosecarvalhoNeto_AmandaDeBritoBarbosa_FabioAurelioBarrosAlexandre_UFRR_2025`
3. Confirme se a pasta `task04/` existe no repositório.

---

## 2) Clonar o repositório no Ubuntu

Abra o Terminal e rode:

```bash
cd ~
git clone https://github.com/amandaabarbosa98/AOC_JosecarvalhoNeto_AmandaDeBritoBarbosa_FabioAurelioBarrosAlexandre_UFRR_2025.git
cd AOC_JosecarvalhoNeto_AmandaDeBritoBarbosa_FabioAurelioBarrosAlexandre_UFRR_2025
ls
Você deve ver a pasta task04/.

---

## 3) Verificar dependências do ambiente
No terminal, verifique:

bash
Copiar código
python3 --version
yosys -V
z3 --version

---

## 4) Executar o pipeline da TASK 04 (gera specs, summary e AST comum)

Na raiz do repositório, execute:

bash
Copiar código
python3 task04/run_task04.py --in task04/inputs_vhdl --out task04 --run-yosys --gen-ast
Saída esperada:

Wrote: task04/results/summary.json

Wrote: task04/results/summary.csv

Confirme os arquivos gerados:

bash
Copiar código
ls task04/specs
ls task04/results
ls task04/results/ast

---

## 5) Abrir o Dashboard (frontend)
Inicie o servidor:

bash
Copiar código
python3 task04/serve_dashboard.py
Abra no navegador:

http://localhost:8000/task04/dashboard/

Para encerrar o servidor: Ctrl + C no terminal.

Obs.: Se aparecer 404 para favicon.ico, isso não afeta o funcionamento.

makefile
Copiar código
::contentReference[oaicite:0]{index=0}
<img width="1259" height="301" alt="image" src="https://github.com/user-attachments/assets/bd4662de-d763-4cb1-aa29-88445bd04fb8" />

Este repositório contém a implementação da TASK 04, com um pipeline automatizado para processar designs em VHDL, extrair propriedades de verificação e gerar artefatos organizados para análise. O foco é tornar o fluxo reproduzível, rastreável e fácil de validar por meio de um resumo consolidado e de um dashboard.

O que foi feito 

Criação dos casos de teste 
Foram criados quatro designs de teste cobrindo os constructs exigidos:

teste_downto: vetores com downto e inversão de índices, com @c2vhdl:ASSERT de equivalência.

teste_integer: portas integer range ..., com @c2vhdl:ASSUME e @c2vhdl:ASSERT.

teste_array: ROM usando array, com asserts condicionais por endereço.

teste_clock: processo sequencial com clock/reset (rising_edge(clk)) e propriedades temporais com $past(...).

Automação do pipeline 
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

Abrir o dashboard
python3 task04/serve_dashboard.py

<img width="1907" height="377" alt="{4DCC15D8-23DC-4707-9740-10DBBDAA3B15}" src="https://github.com/user-attachments/assets/f4d4cd47-4707-4901-9cfb-2bd32147c23e" />

Abra no navegador:

http://localhost:8000/task04/dashboard/

Para parar o servidor: Ctrl + C no terminal.

Observação sobre etapas opcionais (SBY/ESBMC)

O dashboard e o summary podem indicar etapas como SKIP/FAIL quando ferramentas não estão instaladas no ambiente (ex.: vhd2vl, sby, etc.). Mesmo nesses casos, o pipeline mantém a geração dos artefatos principais (specs, summary e Common AST) e registra a causa no campo de notas do resumo.
