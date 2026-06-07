import os
import time
import subprocess
import csv

def rodar_bateria_testes(pasta_instancias="instancias"):
    # script pra rodar em lote e extrair csv pro relatorio
    if not os.path.exists(pasta_instancias):
        print(f"pasta '{pasta_instancias}' nao encontrada. coloque os arquivos .tsp nela.")
        return
        
    arquivos = [f for f in os.listdir(pasta_instancias) if f.endswith(".tsp")]
    if not arquivos:
        print("nao possui nenhum arquivo .tsp na pasta")
        return
        
    print(f"encontradas {len(arquivos)} instancias pra teste")
    resultados = []
    
    for arquivo in arquivos:
        caminho_completo = os.path.join(pasta_instancias, arquivo)
        print(f"testando {arquivo}...")
        
        inicio = time.time()
        
        # roda o solver injetando o conteudo pelo stdin
        try:
            with open(caminho_completo, "r") as f:
                processo = subprocess.run(
                    ["python", "tsp_solver.py"],
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=200 # timeout maximo geral em caso de hang na main
                )
        except Exception as e:
            print(f"erro ao rodar {arquivo}: {e}")
            continue
            
        fim = time.time()
        tempo_gasto = fim - inicio
        
        # captura o custo lendo o stdout
        custo = "ERRO"
        dimensao = "ERRO"
        
        for linha in processo.stdout.splitlines():
            if linha.startswith("TOTAL_WEIGHT:"):
                custo = linha.split(":")[1].strip()
            elif linha.startswith("DIMENSION:"):
                dimensao = linha.split(":")[1].strip()
                
        resultados.append({
            "instancia": arquivo,
            "cidades": dimensao,
            "custo": custo,
            "tempo_s": round(tempo_gasto, 3)
        })
        print(f"-> concluido em {round(tempo_gasto, 3)}s com custo {custo}")
        
    # salva o csv pra gerar as tabelas do relatorio de forma mais pratica
    with open("resultados_avaliacao.csv", mode="w", newline="") as f:
        colunas = ["instancia", "cidades", "custo", "tempo_s"]
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(resultados)
        
    print("testes terminados, salvo em resultados_avaliacao.csv")

if __name__ == "__main__":
    rodar_bateria_testes()
