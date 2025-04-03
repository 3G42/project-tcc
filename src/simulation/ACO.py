import numpy as np
import random
from Circuito_classes import pre_ACO
from program import programa
from src.analysis.utils import drp_drc_define


# Avaliação do custo baseado nas violações de tensão
def calcular_custo(solucao):
    data = programa(option="with-gd-storage", storage_specs=solucao)
    violacoes = data['v_indicators']
    custo_total = violacoes.sum().sum()
    return custo_total


# Inicialização da heurística com base em violações de tensão sem baterias
def calcular_heuristica_inicial():
    data = programa(option="with-gd-without-storage")
    violacoes = data['v_indicators'].copy(True)
    drps, drcs = drp_drc_define(violacoes)
    heuristica = drps + 4 * drcs
    
    heuristica = 1 / (heuristica + 1e-6)  # evitar divisão por zero
    return heuristica.to_dict()

# Geração de uma solução por uma formiga
def construir_solucao(feromonio, heuristica, n_barras, n_baterias, pot_total_max, alpha=1.0, beta=2.0):
    barras_disponiveis = list(range(n_barras))
    probabilidades = []
    for i in barras_disponiveis:
        tau = feromonio[i] ** alpha
        eta = heuristica.get(i, 1.0) ** beta
        probabilidades.append(tau * eta)

    probabilidades = np.array(probabilidades)
    probabilidades /= probabilidades.sum()

    escolhidas = np.random.choice(barras_disponiveis, size=n_baterias, replace=False, p=probabilidades)
    potencias = np.random.dirichlet(np.ones(n_baterias)) * pot_total_max
    energias = potencias * 10  # autonomia fictícia de 10h

    solucao = [[int(b), float(p), float(e)] for b, p, e in zip(escolhidas, potencias, energias)]
    return solucao


# Algoritmo principal ACO
def aco_otimizador(n_baterias, pot_total_max, n_iter=30, n_formigas=20, alpha=1.0, beta=2.0, evaporacao=0.5):
    rede, barras = pre_ACO()
    n_barras = len(barras)
    feromonio = np.ones(n_barras)
    heuristica = calcular_heuristica_inicial()

    melhor_solucao = None
    melhor_custo = float('inf')

    for iteracao in range(n_iter):
        todas_solucoes = []
        for _ in range(n_formigas):
            solucao = construir_solucao(feromonio, heuristica, n_barras, n_baterias, pot_total_max, alpha, beta)
            custo_sol = calcular_custo(solucao)
            todas_solucoes.append((solucao, custo_sol))

            if custo_sol < melhor_custo:
                melhor_solucao = solucao
                melhor_custo = custo_sol

        # Atualização dos feromônios
        feromonio *= (1 - evaporacao)
        for sol, custo_sol in todas_solucoes:
            for barra, _, _ in sol:
                feromonio[barra] += 1.0 / (1 + custo_sol)  # evitar divisão por zero

        print(f"Iteração {iteracao + 1}/{n_iter} - Melhor Custo: {melhor_custo:.2f}")

    return melhor_solucao, melhor_custo


# Exemplo de chamada (você pode ajustar no seu script principal)
if __name__ == "__main__":
    solucao, custo = aco_otimizador(n_baterias=3, pot_total_max=300)
    print("Melhor solução encontrada:", solucao)
    print("Custo associado:", custo)