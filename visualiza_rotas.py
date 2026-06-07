import os
import sys
import math
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# diretorio das instancias e onde salvar as imagens
PASTA_INSTANCIAS = "instancias"
PASTA_IMAGENS = "graficos"

def ler_tsp(caminho):
    # le um arquivo .tsp e retorna o nome, cidades e dimensao
    cidades = []
    nome = "desconhecido"
    dimensao = 0

    with open(caminho, "r") as f:
        linhas = f.read().splitlines()

    lendo_coords = False
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha == "EOF":
            continue
        if linha.startswith("NAME"):
            nome = linha.split(":")[1].strip()
        elif linha.startswith("DIMENSION"):
            dimensao = int(linha.split(":")[1].strip())
        elif linha.startswith("NODE_COORD_SECTION"):
            lendo_coords = True
            continue
        if lendo_coords:
            p = linha.split()
            if len(p) >= 3:
                cidades.append((int(p[0]), float(p[1]), float(p[2])))

    return nome, dimensao, cidades

def ler_tour(caminho):
    # le um arquivo .tour e retorna a sequencia de ids e o custo
    ids = []
    custo = 0

    with open(caminho, "r") as f:
        linhas = f.read().splitlines()

    lendo_tour = False
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha == "EOF":
            continue
        if linha.startswith("TOTAL_WEIGHT"):
            custo = int(linha.split(":")[1].strip())
        elif linha.startswith("TOUR_SECTION"):
            lendo_tour = True
            continue
        if lendo_tour:
            try:
                ids.append(int(linha))
            except ValueError:
                continue

    return ids, custo

def distancia_euc2d(c1, c2):
    dx = c1[1] - c2[1]
    dy = c1[2] - c2[2]
    return math.floor(0.5 + math.sqrt(dx*dx + dy*dy))

def calcular_custo_tour(cidades, ids_tour):
    # calcula o custo total de um tour dado
    # mapeia id -> (id, x, y)
    mapa = {c[0]: c for c in cidades}
    custo = 0
    n = len(ids_tour)
    for i in range(n):
        c1 = mapa[ids_tour[i]]
        c2 = mapa[ids_tour[(i + 1) % n]]
        custo += distancia_euc2d(c1, c2)
    return custo

def plotar_cidades(ax, cidades, titulo="Cidades"):
    # scatter plot das cidades com numeracao
    xs = [c[1] for c in cidades]
    ys = [c[2] for c in cidades]
    ax.scatter(xs, ys, c='#3498db', s=30, zorder=5, edgecolors='#2c3e50', linewidths=0.5)
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

def plotar_tour(ax, cidades, ids_tour, custo, titulo="Tour", cor='#e74c3c'):
    # plota o tour conectando as cidades na ordem
    mapa = {c[0]: c for c in cidades}
    xs = [c[1] for c in cidades]
    ys = [c[2] for c in cidades]

    # cidades
    ax.scatter(xs, ys, c='#3498db', s=25, zorder=5, edgecolors='#2c3e50', linewidths=0.5)

    # arestas do tour
    n = len(ids_tour)
    for i in range(n):
        c1 = mapa[ids_tour[i]]
        c2 = mapa[ids_tour[(i + 1) % n]]
        ax.plot([c1[1], c2[1]], [c1[2], c2[2]], color=cor, linewidth=0.8, alpha=0.7)

    ax.set_title(f"{titulo}\nCusto: {custo}", fontsize=11, fontweight='bold')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

def gerar_tour_vmp(caminho_tsp):
    # roda o solver com timeout curto pra pegar so o vmp (sem ils)
    # truque: seta timeout=1 pra quase nao ter tempo de ils
    try:
        with open(caminho_tsp, "r") as f:
            resultado = subprocess.run(
                ["python", "tsp_solver.py"],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "TSP_TIMEOUT": "1"}
            )
        # parseia a saida
        ids = []
        custo = 0
        lendo = False
        for linha in resultado.stdout.splitlines():
            linha = linha.strip()
            if linha.startswith("TOTAL_WEIGHT"):
                custo = int(linha.split(":")[1].strip())
            elif linha.startswith("TOUR_SECTION"):
                lendo = True
                continue
            elif linha == "EOF":
                break
            elif lendo:
                try:
                    ids.append(int(linha))
                except ValueError:
                    pass
        return ids, custo
    except Exception as e:
        print(f"erro ao gerar tour vmp: {e}")
        return [], 0

def gerar_tour_otimizado(caminho_tsp, timeout=15):
    # roda o solver com timeout maior pra ter ils
    try:
        with open(caminho_tsp, "r") as f:
            resultado = subprocess.run(
                ["python", "tsp_solver.py"],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=timeout + 10,
                env={**os.environ, "TSP_TIMEOUT": str(timeout)}
            )
        ids = []
        custo = 0
        lendo = False
        for linha in resultado.stdout.splitlines():
            linha = linha.strip()
            if linha.startswith("TOTAL_WEIGHT"):
                custo = int(linha.split(":")[1].strip())
            elif linha.startswith("TOUR_SECTION"):
                lendo = True
                continue
            elif linha == "EOF":
                break
            elif lendo:
                try:
                    ids.append(int(linha))
                except ValueError:
                    pass
        return ids, custo
    except Exception as e:
        print(f"erro ao gerar tour otimizado: {e}")
        return [], 0

def comparar_antes_depois(caminho_tsp, nome_saida, timeout_otim=15):
    # gera plot lado a lado: vmp puro vs otimizado
    nome, dim, cidades = ler_tsp(caminho_tsp)
    print(f"gerando comparacao para {nome} ({dim} cidades)...")

    # gera os dois tours
    ids_vmp, custo_vmp = gerar_tour_vmp(caminho_tsp)
    ids_otim, custo_otim = gerar_tour_otimizado(caminho_tsp, timeout_otim)

    if not ids_vmp or not ids_otim:
        print(f"  pulando {nome} - erro ao gerar tours")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"Instância: {nome} ({dim} cidades)", fontsize=14, fontweight='bold')

    plotar_tour(ax1, cidades, ids_vmp, custo_vmp,
                titulo="VMP (Multi-start)", cor='#e74c3c')
    plotar_tour(ax2, cidades, ids_otim, custo_otim,
                titulo="ILS + 2-opt + Or-opt", cor='#27ae60')

    # anota a melhoria
    if custo_vmp > 0:
        melhoria = ((custo_vmp - custo_otim) / custo_vmp) * 100
        fig.text(0.5, 0.02, f"Melhoria: {melhoria:.1f}% (de {custo_vmp} para {custo_otim})",
                ha='center', fontsize=11, color='#2c3e50', fontweight='bold')

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    caminho_img = os.path.join(PASTA_IMAGENS, f"{nome_saida}_comparacao.png")
    plt.savefig(caminho_img, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  salvo em {caminho_img}")

def plotar_tour_unico(caminho_tsp, caminho_tour, nome_saida):
    # plota um tour ja existente (do arquivo .tour)
    nome, dim, cidades = ler_tsp(caminho_tsp)
    ids_tour, custo = ler_tour(caminho_tour)

    if not ids_tour:
        print(f"  tour vazio para {nome}")
        return

    fig, ax = plt.subplots(figsize=(8, 7))
    plotar_tour(ax, cidades, ids_tour, custo,
                titulo=f"{nome} ({dim} cidades)", cor='#2980b9')

    plt.tight_layout()
    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    caminho_img = os.path.join(PASTA_IMAGENS, f"{nome_saida}_tour.png")
    plt.savefig(caminho_img, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  salvo em {caminho_img}")

def plotar_todas_instancias():
    # gera graficos pra todas as instancias da pasta
    if not os.path.exists(PASTA_INSTANCIAS):
        print(f"pasta '{PASTA_INSTANCIAS}' nao encontrada")
        return

    arquivos = sorted([f for f in os.listdir(PASTA_INSTANCIAS) if f.endswith(".tsp") and not f.endswith(".tour")])
    print(f"encontradas {len(arquivos)} instancias\n")

    for arquivo in arquivos:
        caminho = os.path.join(PASTA_INSTANCIAS, arquivo)
        nome_base = arquivo.replace(".tsp", "")

        # 1. plota o tour existente se tiver
        caminho_tour = caminho + ".tour"
        if os.path.exists(caminho_tour):
            plotar_tour_unico(caminho, caminho_tour, nome_base)

        # 2. gera comparacao antes/depois
        # pra instancias menores usa timeout menor pra ser rapido
        nome, dim, _ = ler_tsp(caminho)
        timeout = 10 if dim <= 100 else 20
        comparar_antes_depois(caminho, nome_base, timeout)

    print(f"\ntodos os graficos salvos em '{PASTA_IMAGENS}/'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # modo individual: python visualiza_rotas.py instancias/tsp29.tsp
        caminho = sys.argv[1]
        if os.path.exists(caminho):
            nome_base = os.path.basename(caminho).replace(".tsp", "")
            comparar_antes_depois(caminho, nome_base, timeout_otim=15)
        else:
            print(f"arquivo nao encontrado: {caminho}")
    else:
        # modo batch: gera pra todas as instancias
        plotar_todas_instancias()
