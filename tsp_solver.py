import sys
import math

def read_tsp():
    # le os dados da entrada padrao
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
    # tem que ser floor porque eu testei outra vez e o validador quebra se mudar 1 metro
    dx = c1[1] - c2[1]
    dy = c1[2] - c2[2]
    return math.floor(0.5 + math.sqrt(dx*dx + dy*dy))

def cria_matriz(cidades):
    n = len(cidades)
    matriz = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dist = calcula_distancia(cidades[i], cidades[j])
            matriz[i][j] = dist
            matriz[j][i] = dist
    return matriz

def vizinho_mais_proximo(matriz, inicio=0):
    # aquele logico guloso padrao, vai pro mais perto ate fechar
    n = len(matriz)
    nao_visitados = set(range(n))
    rota = [inicio]
    nao_visitados.remove(inicio)
    
    atual = inicio
    custo_total = 0
    
    while nao_visitados:
        menor_dist = 999999999 # valor absurdamente grande simulando inifnito
        proxima = -1
        
        for cand in nao_visitados:
            dist = matriz[atual][cand]
            if dist < menor_dist:
                menor_dist = dist
                proxima = cand
                
        rota.append(proxima)
        custo_total += menor_dist
        nao_visitados.remove(proxima)
        atual = proxima
        
    # professor avisou tem q voltar pra primeira senao nao e ciclo 
    custo_total += matriz[atual][inicio]
    
    return rota, custo_total

def formata_saida(nome, tamanho, custo, rota, cidades):
    # o professor exige essa formatacao cravada
    print(f"NAME: {nome}")
    print("COMMENT: solucao base vmp - gusttavo")
    print("TYPE: TOUR")
    print(f"DIMENSION: {tamanho}")
    print(f"TOTAL_WEIGHT: {custo}")
    print("TOUR_SECTION")
    
    # printar a ordem da rota pelos id real das cidades e nao o indice i
    for idx_cidade in rota:
        id_real = cidades[idx_cidade][0]
        print(id_real)
        
    print("EOF")

if __name__ == "__main__":
    nome, tamanho, cidades = read_tsp()
    if tamanho > 0:
        matriz_dist = cria_matriz(cidades)
        
        # geramos a primeira solucao a partir do 0 mesmo
        melhor_rota, melhor_custo = vizinho_mais_proximo(matriz_dist)
        
        # printa exatamente como pedem
        formata_saida(nome, tamanho, melhor_custo, melhor_rota, cidades)
