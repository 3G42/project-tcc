import random
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from deap import base, creator, tools

from src.analysis.utils import drp_drc_define
from src.simulation.program import programa

# === DEAP Setup ===
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()


def rodar_ga(
        N_BATERIAS,
        P_TOTAL_MAX,
        E_TOTAL_MAX,
        POP_SIZE,
        GERACOES,

):
    N_BARRAS = 15
    P_MAX = P_TOTAL_MAX / N_BATERIAS
    E_MAX = E_TOTAL_MAX / N_BATERIAS

    TAXA_MUT = 0.15
    ELITISMO = True

    start_case = programa(option="without-gd-storage")
    drps_start_case, drcs_start_case = drp_drc_define(start_case['v_indicators'])
    max_drp_start = drps_start_case.max()
    max_drc_start = drcs_start_case.max()

    # --- Inicialização do indivíduo ---
    def init_individual():
        b = random.sample(range(1, N_BARRAS + 1), N_BATERIAS)
        p = [random.uniform(0, P_MAX) for _ in range(N_BATERIAS)]
        e = [random.uniform(0, E_MAX) for _ in range(N_BATERIAS)]
        return creator.Individual((b, p, e))

    # --- Avaliação (Fitness) ---
    def evaluate(individuo):
        barras, potencias, energias = individuo
        storage_specs = []

        # Penaliza dimensionamentos inválidos
        for idx in range(len(barras)):
            p = potencias[idx]
            e = energias[idx]
            if p < 5 or e < 25 or p > e:
                return (1e6,)
            storage_specs.append([barras[idx], potencias, energias])

        # Simulação real
        try:
            resultado = programa('with-gd-storage', storage_specs)
        except Exception as err:
            print("Erro na simulação:", err)
            return (1e6,)  # penalização por falha de simulação

        indicadores = resultado['v_indicators']
        feeder_losses = resultado['feeder_losses']

        drps, drcs = drp_drc_define(indicadores)

        soma_pot = sum(potencias)
        soma_ener = sum(energias)

        # PESOS ajustáveis
        PESO_DRC = 1000
        PESO_DRP = 100
        PESO_POT = 1.0
        PESO_ENER = 0.33

        fitness = (
                drcs.sum() * PESO_DRC +
                drps.sum() * PESO_DRP +
                soma_pot * PESO_POT +
                soma_ener * PESO_ENER
        )

        return (fitness,)

    # --- Operadores Genéticos ---
    def crossover(ind1, ind2):
        corte1, corte2 = sorted(random.sample(range(N_BATERIAS), 2))

        # Crossover de ordem para as barras
        child_barras = [None] * N_BATERIAS
        child_barras[corte1:corte2] = ind1[0][corte1:corte2]

        ptr = 0
        for b in ind2[0]:
            if b not in child_barras:
                # Encontra próxima posição vazia
                while ptr < N_BATERIAS and child_barras[ptr] is not None:
                    ptr += 1
                if ptr < N_BATERIAS:
                    child_barras[ptr] = b
                else:
                    break  # Evita ultrapassar o limite

        # Crossover aritmético para potência e energia
        alpha = random.random()
        child_pot = [alpha * a + (1 - alpha) * b for a, b in zip(ind1[1], ind2[1])]
        child_ener = [alpha * a + (1 - alpha) * b for a, b in zip(ind1[2], ind2[2])]

        return creator.Individual((child_barras, child_pot, child_ener)),

    def mutate(ind):
        barras, potencias, energias = ind
        # Mutação de barras (substituição única)
        if random.random() < TAXA_MUT:
            idx = random.randint(0, N_BATERIAS - 1)
            disponiveis = list(set(range(1, N_BARRAS + 1)) - set(barras))
            if disponiveis:
                barras[idx] = random.choice(disponiveis)

        # Mutação gaussiana de potência e energia
        for idx in range(N_BATERIAS):
            if random.random() < TAXA_MUT:
                potencias[idx] = np.clip(potencias[idx] + random.gauss(0, P_MAX * 0.1), 0, P_MAX)
            if random.random() < TAXA_MUT:
                energias[idx] = np.clip(energias[idx] + random.gauss(0, E_MAX * 0.1), 0, E_MAX)

        return ind,

    toolbox.register("individual", init_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", crossover)
    toolbox.register("mutate", mutate)
    toolbox.register("select", tools.selTournament, tournsize=2)

    # --- Execução principal ---

    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("min", np.min)

    historico = []
    melhores_por_geracao = []

    for g in range(GERACOES):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        # Crossover
        for i in range(1, len(offspring), 2):
            if i + 1 < len(offspring):
                child1, = toolbox.mate(offspring[i - 1], offspring[i])
                offspring[i - 1][:] = child1[:]

        # Mutação
        for mutant in offspring:
            toolbox.mutate(mutant)

        # Avaliação
        for ind in offspring:
            ind.fitness.values = toolbox.evaluate(ind)

        # Elitismo
        if ELITISMO:
            best = tools.selBest(pop, 1)[0]
            offspring[0] = toolbox.clone(best)

        pop[:] = offspring
        hof.update(pop)

        melhor = tools.selBest(pop, 1)[0]
        melhor_fitness = melhor.fitness.values[0]

        historico.append(melhor_fitness)
        melhores_por_geracao.append((toolbox.clone(melhor), melhor_fitness))

        print(f"Geração {g}: Melhor individuo {melhor}  Fitness = {melhor_fitness:.4f}  Potencia = {sum(melhor[1])}")

    # Resultados
    melhor = hof[0]
    barras, potencias, energias = melhor
    for i in range(N_BATERIAS):
        print(f"Barra {barras[i]}: Potência = {potencias[i]:.2f} kW, Energia = {energias[i]:.2f} kWh")

    return melhores_por_geracao


if __name__ == "__main__":
    rodar_ga(N_BATERIAS=2, P_TOTAL_MAX=200, E_TOTAL_MAX=400, POP_SIZE=50, GERACOES=120)
