import itertools
from datetime import timedelta
import time
import pandas as pd

from src.simulation.program import programa


def gerar_solucoes_possiveis(n_barras, max_baterias, pot_total_max, delta_pot):
    # Garante que delta_pot seja múltiplo de 5
    if delta_pot % 5 != 0:
        raise ValueError("O delta_pot deve ser múltiplo de 5 para atender à restrição de potência mínima.")

    # Lista de índices das barras (0 a n_barras - 1)
    todas_barras = list(range(n_barras))

    # Lista para armazenar soluções válidas: (vetor de potências)
    solucoes_validas = []

    # Loop: quantidade de baterias de 1 até o máximo
    for k in range(1, max_baterias + 1):
        # Gera todas as combinações de k barras
        combinacoes_barras = itertools.combinations(todas_barras, k)

        for barras in combinacoes_barras:
            # Gera potências possíveis (múltiplos de 5 e do delta)
            potencias_possiveis = list(range(0, pot_total_max + delta_pot, delta_pot))
            potencias_possiveis = [p for p in potencias_possiveis if p % 5 == 0]

            # Gera todas as distribuições de potência entre essas k barras
            combinacoes_potencias = itertools.product(potencias_possiveis, repeat=k)

            for potencias in combinacoes_potencias:
                soma_pot = sum(potencias)

                # Validação: soma total válida e nenhuma bateria com potência negativa
                if 0 < soma_pot <= pot_total_max:
                    # Cria vetor com potência zero para barras sem bateria
                    vetor_potencias = [0] * n_barras
                    for i, barra in enumerate(barras):
                        vetor_potencias[barra] = potencias[i]

                    # Adiciona solução
                    solucoes_validas.append(vetor_potencias)

    return solucoes_validas

def avaliar_fitness(v_indicators: pd.DataFrame, is_start=False):
    # v_indicators: DataFrame com índices ['DRP_A', 'DRP_B', ...]
    drcs = v_indicators.loc[["DRC_A", "DRC_B", "DRC_C"]]
    drps = v_indicators.loc[["DRP_A", "DRP_B", "DRP_C"]]

    if is_start:
        return 20 * drcs.sum().sum() + 5 * drps.sum().sum()

    fitness = (
        20 * drcs.max().max() +  # máximo entre as fases
        5 * drps.max().max()
    )
    return fitness

def executar_todas_solucoes_com_fitness():
    # Parâmetros do problema
    n_barras = 15
    max_baterias = 3
    pot_total_max = 150
    delta_pot = 25
    fator_energia = 2

    # Gera todas as soluções
    solucoes = gerar_solucoes_possiveis(
        n_barras=n_barras,
        max_baterias=max_baterias,
        pot_total_max=pot_total_max,
        delta_pot=delta_pot
    )

    total = len(solucoes)
    resultados = []
    inicio_global = time.time()

    for i, solucao in enumerate(solucoes):
        t_inicio = time.time()

        storage_specs = []
        for barra, pot in enumerate(solucao):
            if pot > 0:
                energia = pot * fator_energia
                storage_specs.append([barra, pot, energia])

        dados = programa(option="with-gd-storage", storage_specs=storage_specs)
        fitness = avaliar_fitness(dados["v_indicators"])

        resultado = {
            "id": i,
            "storage_specs": storage_specs,
            "fitness": fitness,
            "feeder_energy": dados["feeder_energy"],
            "feeder_losses": dados["feeder_losses"],
            "v_indicators": dados["v_indicators"]
        }

        resultados.append(resultado)

        # Tempo por simulação
        duracao = time.time() - t_inicio
        media = (time.time() - inicio_global) / (i + 1)
        restante = media * (total - (i + 1))

        print(
            f"Solução {i + 1}/{total} | Fitness: {fitness:.2f} | Tempo desta: {duracao:.1f}s | "
            f"Est. restante: {timedelta(seconds=int(restante))}"
        )
    return resultados

if __name__ == "__main__":
    resultados = executar_todas_solucoes_com_fitness()

    # Ordenar pelas melhores soluções
    resultados_ordenados = sorted(resultados, key=lambda x: x['fitness'])

    # Mostrar top 5
    for r in resultados_ordenados[:5]:
        print(f"Fitness: {r['fitness']:.2f} | Specs: {r['storage_specs']}")