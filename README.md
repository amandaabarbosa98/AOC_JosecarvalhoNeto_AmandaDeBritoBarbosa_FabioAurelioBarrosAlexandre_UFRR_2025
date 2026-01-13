# Projeto – Automação de Pipeline para Verificação Formal de Circuitos em VHDL

Este repositório contém os artefatos, códigos e resultados do Projeto Final de Arquitetura e Organização de Computadores. O projeto investiga, implementa e automatiza um fluxo de **Verificação Formal de Hardware** utilizando ferramentas *Open Source*.

O projeto foi realizado pelos alunos **Amanda de Brito**, **Fábio Aurélio** e **José Carvalho**, com auxílio do **Prof. Dr. Herbert Rocha** pelo Departamento de Ciência da Computação na Universidade Federal de Roraima, em 2025.

---

## 💭 Motivação

A verificação de circuitos digitais complexos apenas via simulação (testbench) é insuficiente para garantir a ausência de erros críticos. A Verificação Formal oferece uma prova matemática de correção, mas as ferramentas comerciais são caras e inacessíveis.

A literatura propõe fluxos que traduzem Hardware (VHDL) para Software (C) para aproveitar verificadores poderosos como o **ESBMC**. No entanto, esses fluxos frequentemente dependem de ferramentas legadas ou configurações manuais propensas a erros.

## 🎯 Objetivos

1.  **Automatizar o Pipeline:** Desenvolver um script capaz de ler código VHDL, extrair regras de negócio (`assertions`) e orquestrar as ferramentas de verificação sem intervenção humana.
2.  **Validar o Fluxo de Hardware:** Integrar **Yosys + SymbiYosys** para realizar a síntese e verificação formal de propriedades em nível de RTL.
3.  **Analisar o Fluxo de Software:** Testar a viabilidade da tradução VHDL $\to$ C para uso com o **ESBMC**.
4.  **Propor Nova Arquitetura:** Demonstrar as limitações da tradução baseada em arquivos e propor um fluxo unificado via *Frontend* GHDL.

## 🛠️ Tecnologias e Ferramentas

O pipeline foi construido sobre o ecossistema Linux (WSL2/Ubuntu) utilizando:
- Linguagem de Script: Python 3 (com Regex para extração de metadados).
- Síntese e Otimização: Yosys.
- Verificação de Hardware: SymbiYosys (SBY) com solver Z3.
- Verificação de Software: ESBMC.
- Frontend VHDL: GHDL

## 📁 Estrutura do Respositório

```text
├── task04                              # Etapa de aplicação do GHDL/AST
├── teste_integer/                      # Teste de restrição de inteiros
|   ├── Teste 1
|   └── Teste 2                    
├── teste_clock/                        # Teste de lógica sequencial/temporal
|   ├── Teste 1
|   └── Teste 2                         
├── teste_downto/                       # Teste de vetores e direção de bits
|   ├── Teste 1
|   └── Teste 2                        
├── teste_array/                        # Teste de complexidade
|   ├── Teste 1
|   └── Teste 2                         
├── relatorio_aoc_projeto-final.pdf     # Documentação e Relatório
├── automacao_inicial.py                # Script de automação inicial
└── README.md                           # Este arquivo
```

## 📂 Estrutura dos Diretórios

## Teste 1
Nesse primeiro teste, elaboramos circuitos em VHDL simples que não possuiam regras e tags. Inicialmente, os circuitos passaram pela tradução de VHDL para Verilog (gerando o arquivo com extensão .v) com a
ferramenta *VHD2VL* e em seguida, a síntese/limpeza pela ferramenta *Yosys* (gerando o arquivo elaborado_{circuito}.v), para posteriormente passar pela ferramenta de validação matemática *SymbiYosys*.

## Teste 2
Nesse segundo teste, adicionamos as tags nos mesmos circuitos para verificar a diferença que ocorreria na existência e
ausência delas. Assim como no primeiro teste, o código em VHDL foi traduzido para Verilog, porém a tradução ocorreu internamente na ferramenta *SymbiYosys*.  

O circuito também passou por validação matemática com o *SymbiYosys*, testado pelo solver *Z3* contido no programa.
Foi feito um teste de falha proposital, com a expectativa que a ferramenta usada para validação
pudesse acusar erro/divergência entre as regras/tags e o circuito proposto.

---

# Tutorial — (GitHub → Ubuntu → Execução → Dashboard)

Este repositório contém a implementação da TASK 04, com um pipeline automatizado para processar designs em VHDL, extrair propriedades de verificação e gerar artefatos organizados para análise. O foco é tornar o fluxo reproduzível, rastreável e fácil de validar por meio de um resumo consolidado e de um dashboard.  

<img width="1259" height="301" alt="image" src="https://github.com/user-attachments/assets/bd4662de-d763-4cb1-aa29-88445bd04fb8" />

---
Este guia mostra como acessar o repositório no GitHub, clonar no Ubuntu, executar o pipeline da TASK 04 e abrir o dashboard localmente.

## 1) Clonar o repositório no Ubuntu

Abra o Terminal e rode:

```bash
> cd ~
> git clone https://github.com/amandaabarbosa98/AOC_JosecarvalhoNeto_AmandaDeBritoBarbosa_FabioAurelioBarrosAlexandre_UFRR_2025.git
> cd AOC_JosecarvalhoNeto_AmandaDeBritoBarbosa_FabioAurelioBarrosAlexandre_UFRR_2025
> ls
```
Você deve ver a pasta task04/.


## 2) Verificar dependências do ambiente
No terminal, verifique:

```bash
> python3 --version
> yosys -V
> z3 --version
```


## 3) Executar o pipeline da TASK 04 (gera specs, summary e AST comum)

Na raiz do repositório, execute:

```bash
> python3 task04/run_task04.py --in task04/inputs_vhdl --out task04 --run-yosys --gen-ast
```

Saída esperada:

```bash
Wrote: task04/results/summary.json
Wrote: task04/results/summary.csv
```

Confirme os arquivos gerados:

```bash
> ls task04/specs
> ls task04/results
> ls task04/results/ast
```


## 4) Abrir o Dashboard (frontend)
Inicie o servidor:

```bash
> python3 task04/serve_dashboard.py
```

Abra no navegador:
```bash
> http://localhost:8000/task04/dashboard/
```

Para encerrar o servidor: Ctrl + C no terminal.
Obs.: Se aparecer 404 para favicon.ico, isso não afeta o funcionamento.

---

## O que foi feito
### Criação dos casos de teste 
Foram criados quatro designs de teste cobrindo os constructs exigidos:
- teste_downto: vetores com downto e inversão de índices, com @c2vhdl:ASSERT de equivalência.
- teste_integer: portas integer range ..., com @c2vhdl:ASSUME e @c2vhdl:ASSERT.
- teste_array: ROM usando array, com asserts condicionais por endereço.
- teste_clock: processo sequencial com clock/reset (rising_edge(clk)) e propriedades temporais com $past(...).

### Automação do pipeline 
O script task04/run_task04.py detecta os VHDL, extrai portas e tags @c2vhdl:ASSUME/@c2vhdl:ASSERT, gera um arquivo auxiliar por design em task04/specs/*.json e consolida resultados em:
- task04/results/summary.json
- task04/results/summary.csv

### AST comum (Objetivo 5)
Para cada design é gerado um arquivo task04/results/ast/<design>.ast.json com schema:
- aoc-task04-common-ast-v1
Esse Common AST reúne: metadados, interface (ports), propriedades (properties) e estrutura quando disponível (wires/cells/stats).

### Dashboard (frontend)
O dashboard (servido por task04/serve_dashboard.py) lê summary.json e mostra o status por etapa e por design, com links para spec.json e ast.json.

### Estrutura principal
- task04/inputs_vhdl/ — VHDLs de teste com tags @c2vhdl:ASSUME/@c2vhdl:ASSERT
- task04/specs/ — arquivos auxiliares gerados (*.json)
- task04/results/ — summary.json, summary.csv e ast/*.ast.json
- task04/run_task04.py — script principal do pipeline
- task04/serve_dashboard.py + task04/dashboard/ — frontend (dashboard)
- task04/unify_ast.py + task04/ast_frontend/ — geração/unificação do AST comum

### Como executar

Abrir o dashboard
```
python3 task04/serve_dashboard.py
```
Abra no navegador:
```
http://localhost:8000/task04/dashboard/
```

<img width="1907" height="377" alt="{4DCC15D8-23DC-4707-9740-10DBBDAA3B15}" src="https://github.com/user-attachments/assets/f4d4cd47-4707-4901-9cfb-2bd32147c23e" />

Para parar o servidor: Ctrl + C no terminal.

## Observação sobre etapas opcionais (SBY/ESBMC)
O dashboard e o summary podem indicar etapas como SKIP/FAIL quando ferramentas não estão instaladas no ambiente (ex.: vhd2vl, sby, etc.). Mesmo nesses casos, o pipeline mantém a geração dos artefatos principais (specs, summary e Common AST) e registra a causa no campo de notas do resumo.
