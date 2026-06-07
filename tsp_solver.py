import sys
import math
import time
import random
import os

# tempo maximo padrao em segundos, margem de seguranca pro timeout do professor
# da pra mudar com variavel de ambiente pra testes rapidos: set TSP_TIMEOUT=10
TEMPO_LIMITE = int(os.environ.get("TSP_TIMEOUT", 175))

def read_tsp():
    # le os dados da entrada padrao no formato tsplib
    cidades = []
    tamanho = 0
    nome_instancia = "desconhecido"

    linhas = sys.stdin.read().splitlines()
    lendo_coords = False

    for linha in linhas:
        linha = linha.strip()
        if not linha or linha == "EOF":
            continue

        if linha.startswith("NAME"):
            partes = linha.split(":")
            if len(partes) > 1:
                nome_instancia = partes[1].strip()
        elif linha.startswith("DIMENSION"):
            partes = linha.split(":")
            if len(partes) > 1:
                tamanho = int(partes[1].strip())
        elif linha.startswith("NODE_COORD_SECTION"):
            lendo_coords = True
            continue

        if lendo_coords:
            p = linha.split()
            if len(p) >= 3:
                id_cidade = int(p[0])
                x = float(p[1])
                y = float(p[2])
                cidades.append((id_cidade, x, y))

    return nome_instancia, tamanho, cidades

def calcula_distancia(c1, c2):
    # tem que ser floor pq testei e o validador quebra se mudar
    dx = c1[1] - c2[1]
    dy = c1[2] - c2[2]
    return math.floor(0.5 + math.sqrt(dx*dx + dy*dy))

def cria_matriz(cidades):
    # pre calcula todas distancias pra nao ficar calculando td hora
    n = len(cidades)
    matriz = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dist = calcula_distancia(cidades[i], cidades[j])
            matriz[i][j] = dist
            matriz[j][i] = dist
    return matriz

def custo_rota(rota, matriz):
    # soma todas as arestas do ciclo fechado
    n = len(rota)
    total = 0
    for k in range(n):
        total += matriz[rota[k]][rota[(k + 1) % n]]
    return total

def vizinho_mais_proximo(matriz, inicio=0):
    # aquele logico guloso padrao, vai pro mais perto ate fechar
    n = len(matriz)
    nao_visitados = set(range(n))
    rota = [inicio]
    nao_visitados.remove(inicio)

    atual = inicio
    custo_total = 0

    while nao_visitados:
        menor_dist = float('inf')
        proxima = -1

        for cand in nao_visitados:
            if matriz[atual][cand] < menor_dist:
                menor_dist = matriz[atual][cand]
                proxima = cand

        rota.append(proxima)
        custo_total += menor_dist
        nao_visitados.remove(proxima)
        atual = proxima

    # voltar pro inicio pra fechar o ciclo
    custo_total += matriz[atual][inicio]

    return rota, custo_total

def multi_start_vmp(matriz, tempo_max):
    # roda o vmp de varias cidades e pega o melhor resultado
    # pra nao depender de sorte de qual cidade comeca
    n = len(matriz)
    melhor_rota = None
    melhor_custo = float('inf')

    # pra instancias grandes testa um subconjunto aleatorio senao demora
    if n > 200:
        qtd = min(60, n)
        candidatos = random.sample(range(n), qtd)
    else:
        candidatos = list(range(n))

    for inicio in candidatos:
        if time.time() > tempo_max:
            break
        rota, custo = vizinho_mais_proximo(matriz, inicio)
        if custo < melhor_custo:
            melhor_custo = custo
            melhor_rota = rota[:]

    return melhor_rota, melhor_custo

def dois_opt(rota, matriz, tempo_max):
    # 2-opt: descruzamento de arestas, fica rodando ate parar de melhorar
    # first-improvement pra cada passada pq full scan demora demais
    melhor = rota[:]
    n = len(melhor)
    melhorou = True

    while melhorou:
        melhorou = False
        if time.time() > tempo_max:
            break

        for i in range(1, n - 1):
            if time.time() > tempo_max:
                break
            for j in range(i + 1, n):
                # calcula se trocar as arestas (i-1,i) e (j,j+1) melhora
                a, b = melhor[i - 1], melhor[i]
                c, d = melhor[j], melhor[(j + 1) % n]

                ganho = (matriz[a][b] + matriz[c][d]) - (matriz[a][c] + matriz[b][d])

                if ganho > 0:
                    # inverte o pedaco de i ate j pra descruzar
                    melhor[i:j+1] = reversed(melhor[i:j+1])
                    melhorou = True
                    break
            if melhorou:
                break

    return melhor, custo_rota(melhor, matriz)

def realoca_cidades(rota, matriz, tempo_max):
    # or-opt simplificado: pega cada cidade e ve se tem lugar melhor pra ela
    # tipo aquele jogo de deslizar pecas, so que com cidades
    n = len(rota)
    melhorou = True

    while melhorou:
        melhorou = False
        if time.time() > tempo_max:
            break

        for i in range(n):
            if time.time() > tempo_max:
                break

            prev_i = (i - 1) % n
            next_i = (i + 1) % n
            ci = rota[i]

            # quanto ganha removendo ci da posicao atual
            economia = (matriz[rota[prev_i]][ci] +
                       matriz[ci][rota[next_i]] -
                       matriz[rota[prev_i]][rota[next_i]])

            melhor_custo_ins = float('inf')
            melhor_pos = -1

            for j in range(n):
                if j == prev_i or j == i or j == next_i:
                    continue

                next_j = (j + 1) % n
                # custo de colocar ci entre rota[j] e rota[next_j]
                custo_ins = (matriz[rota[j]][ci] +
                            matriz[ci][rota[next_j]] -
                            matriz[rota[j]][rota[next_j]])

                if custo_ins < melhor_custo_ins:
                    melhor_custo_ins = custo_ins
                    melhor_pos = j

            # se inserir em outro lugar e mais barato do que manter
            if melhor_pos >= 0 and melhor_custo_ins < economia:
                # salva o id da cidade destino antes de mexer na lista
                alvo = rota[melhor_pos]
                rota.pop(i)
                # acha o destino pelo valor pq o indice muda com o pop
                pos_alvo = rota.index(alvo)
                rota.insert(pos_alvo + 1, ci)
                n = len(rota)
                melhorou = True
                break

    return rota, custo_rota(rota, matriz)

def busca_local(rota, matriz, tempo_max):
    # combina 2-opt e realocacao ate estabilizar
    custo_anterior = float('inf')
    custo_atual = custo_rota(rota, matriz)

    while custo_atual < custo_anterior:
        if time.time() > tempo_max:
            break
        custo_anterior = custo_atual

        rota, _ = dois_opt(rota, matriz, tempo_max)
        rota, _ = realoca_cidades(rota, matriz, tempo_max)
        custo_atual = custo_rota(rota, matriz)

    return rota, custo_atual

def double_bridge(rota):
    # perturbacao classica do ils: corta a rota em 4 pedacos e remonta diferente
    # isso faz um salto grande no espaco de busca pra sair de otimo local
    n = len(rota)
    cortes = sorted(random.sample(range(1, n), 3))

    p1 = rota[:cortes[0]]
    p2 = rota[cortes[0]:cortes[1]]
    p3 = rota[cortes[1]:cortes[2]]
    p4 = rota[cortes[2]:]

    # reconecta na ordem 1-3-2-4 pra baguncar bem
    return p1 + p3 + p2 + p4

def ils(rota_inicial, custo_inicial, matriz, tempo_max):
    # iterated local search: perturba e otimiza em loop ate acabar o tempo
    # essa eh a parte que faz a solucao ficar competitiva de verdade
    melhor_rota = rota_inicial[:]
    melhor_custo = custo_inicial
    rota_atual = rota_inicial[:]

    while time.time() < tempo_max:
        # perturbacao double bridge pra escapar do otimo local
        rota_nova = double_bridge(rota_atual)

        # busca local completa na rota perturbada
        rota_nova, custo_novo = busca_local(rota_nova, matriz, tempo_max)

        # criterio de aceitacao: so aceita se melhorou
        if custo_novo < melhor_custo:
            melhor_rota = rota_nova[:]
            melhor_custo = custo_novo
            rota_atual = rota_nova[:]
        else:
            # volta pro melhor e tenta perturbar de novo
            rota_atual = melhor_rota[:]

    return melhor_rota, melhor_custo

def formata_saida(nome, tamanho, custo, rota, cidades):
    # formatacao exigida pelo professor
    print(f"NAME: {nome}")
    print("COMMENT: Luiz Gusttavo Macedo Magalhaes - metodo ILS com VMP multi-start e 2-opt")
    print("TYPE: TOUR")
    print(f"DIMENSION: {tamanho}")
    print(f"TOTAL_WEIGHT: {custo}")
    print("TOUR_SECTION")

    # printa o id real de cada cidade, nao o indice do array
    for idx in rota:
        print(cidades[idx][0])

    print("EOF")

if __name__ == "__main__":
    random.seed(42)  # seed fixa pra resultado reproduzivel

    nome, tamanho, cidades = read_tsp()

    if tamanho > 0:
        inicio = time.time()
        fim = inicio + TEMPO_LIMITE

        # monta a matriz de distancias
        matriz = cria_matriz(cidades)

        n = len(cidades)

        # fase 1: multi-start vmp pra achar boa rota inicial
        # gasta no max 5% do tempo nisso, eh rapido
        rota, custo = multi_start_vmp(matriz, inicio + TEMPO_LIMITE * 0.05)

        # fase 2: busca local na melhor rota do vmp
        # gasta uns 25% do tempo otimizando a primeira solucao
        rota, custo = busca_local(rota, matriz, inicio + TEMPO_LIMITE * 0.25)

        # fase 3: ils com o tempo restante (so se tiver pelo menos 4 cidades)
        # double bridge precisa de 3 cortes entao n >= 4
        if n >= 4:
            # para 2 segundos antes do limite pra garantir que printa a saida
            rota, custo = ils(rota, custo, matriz, fim - 2)

        # printa exatamente como pedem
        formata_saida(nome, tamanho, custo, rota, cidades)
