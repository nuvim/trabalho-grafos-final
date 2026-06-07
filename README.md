# Solver PCV (Problema do Caixeiro Viajante)

**Disciplina:** Algoritmos em Grafos  
**Aluno:** Luiz Gusttavo Macedo Magalhães — Matrícula 556217  

Este repositório contém a solução desenvolvida para o Trabalho Prático Final do Problema do Caixeiro Viajante (PCV / TSP). O objetivo é encontrar um ciclo hamiltoniano de custo mínimo para instâncias da TSPLIB.

---

## Heurísticas Implementadas

A solução utiliza uma combinação de heurísticas construtivas e métodos de busca local/metaheurísticas, sendo eles:

1. **Multi-Start VMP (Vizinho Mais Próximo):** Heurística gulosa construtiva executada a partir de múltiplas cidades de origem.
2. **2-opt (First-improvement):** Busca local para descruzar arestas.
3. **Or-opt-1:** Busca local para realocação de cidades individuais.
4. **Iterated Local Search (ILS):** Metaheurística que utiliza perturbação *Double-Bridge* para escapar de ótimos locais.

O script divide o tempo disponível inteligente (timeout em ~175s para garantir saída antes do limite) entre essas etapas.

---

## Requisitos

O projeto utiliza apenas bibliotecas padrão do Python (sem dependências externas de grafos).
- Python 3.8 ou superior
- Opcional: `matplotlib` apenas para rodar o script de geração de imagens (`visualiza_rotas.py`)

---

## Como Executar

O solver foi projetado estritamente conforme as regras: lê de `stdin` e imprime no `stdout`.

### 1. Execução Simples (Facilitada)
Para facilitar, você pode usar o script `rodar.bat` informando o arquivo:
```cmd
rodar.bat tsp29.tsp
```
Ou rodar manualmente redirecionando a saída:
```cmd
python tsp_solver.py < instancias/tsp29.tsp > tsp29.tsp.tour
```

### 2. Configurando Timeout para Testes (Opcional)
Se quiser testar rápido sem esperar a busca até o fim, configure a variável de ambiente `TSP_TIMEOUT` (em segundos) antes de rodar:
- **Windows (PowerShell):** `$env:TSP_TIMEOUT="15"; python tsp_solver.py < instancias/tsp29.tsp`
- **Linux/Mac:** `TSP_TIMEOUT=15 python tsp_solver.py < instancias/tsp29.tsp`

### 3. Rodar a Bateria Completa de Testes
Para processar todos os `.tsp` da pasta `instancias/` e gerar um relatório num CSV (`resultados_bateria.csv`):
```bash
python testa_instancias.py
```

### 4. Visualizar Rotas
Para gerar gráficos comparando a solução inicial (VMP) com a final (ILS), rode o arquivo de visualização (requer matplotlib instalado):
```bash
python visualiza_rotas.py
```
*(Os PNGs serão salvos na pasta `graficos/`)*

---

## Estrutura de Diretórios

- `/` (Raiz)
  - `tsp_solver.py`: O código-fonte principal (Solver)
  - `testa_instancias.py`: Script automatizado de testes
  - `visualiza_rotas.py`: Script para plotar os gráficos do antes/depois
- `/instancias/`: Arquivos TSPLIB originais (`.tsp`) e arquivos de tour do professor (`.tour`)
- `/graficos/`: Imagens geradas pela visualização
- `/material/`: Documentos de apoio fornecidos pelo professor (especificações e bibliografia)

