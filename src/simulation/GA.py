import random
import numpy as np
import matplotlib.pyplot as plt
from deap import base, creator, tools

from program import programa
from utils import drp_drc_define



# === Parâmetros do problema ===
N_BARRAS = 15
N_BATERIAS = 3
P_TOTAL_MAX = 200
E_TOTAL_MAX = 400
P_MAX = P_TOTAL_MAX/N_BATERIAS
E_MAX = E_TOTAL_MAX/N_BATERIAS
POP_SIZE = 100
GERACOES = 200
TAXA_MUT = 0.15
ELITISMO = True

start_case = programa(option="without-gd-storage")
drps_start_case, drcs_start_case = drp_drc_define(start_case['v_indicators'])
max_drp_start = drps_start_case.max()
max_drc_start = drcs_start_case.max()


# === DEAP Setup ===
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# --- Inicialização do indivíduo ---
def init_individual():
    barras = random.sample(range(1, N_BARRAS + 1), N_BATERIAS)
    potencias = [random.uniform(0, P_MAX) for _ in range(N_BATERIAS)]
    energias = [random.uniform(0, E_MAX) for _ in range(N_BATERIAS)]
    return creator.Individual((barras, potencias, energias))

toolbox.register("individual", init_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# --- Avaliação (Fitness) ---
def evaluate(ind):
    barras, potencias, energias = ind
    storage_specs = []

    # Penaliza dimensionamentos inválidos
    for i in range(len(barras)):
        p = potencias[i]
        e = energias[i]
        if p < 5 or e < 25 or p > e:
            return (1e6,)
        storage_specs.append([barras[i], p, e])

    # Simulação real
    try:
        resultado = programa('with-gd-storage', storage_specs)
    except Exception as e:
        print("Erro na simulação:", e)
        return (1e6,)  # penalização por falha de simulação

    indicadores = resultado['v_indicators']
    feeder_losses = resultado['feeder_losses']
    drps, drcs = drp_drc_define(indicadores)

    # Considerar apenas melhorias reais
    drps = np.maximum(drps - drps_start_case, 0)
    drcs = np.maximum(drcs - drcs_start_case, 0)

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


toolbox.register("evaluate", evaluate)

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
    for i in range(N_BATERIAS):
        if random.random() < TAXA_MUT:
            potencias[i] = np.clip(potencias[i] + random.gauss(0, P_MAX * 0.1), 0, P_MAX)
        if random.random() < TAXA_MUT:
            energias[i] = np.clip(energias[i] + random.gauss(0, E_MAX * 0.1), 0, E_MAX)

    return ind,

toolbox.register("mate", crossover)
toolbox.register("mutate", mutate)
toolbox.register("select", tools.selTournament, tournsize=2)

# --- Execução principal ---
def main():
    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("min", np.min)

    historico = []

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
        print(f"Geração {g}: Melhor individuo {melhor}  Fitness = {melhor_fitness:.4f}")

    # Resultados
    melhor = hof[0]
    barras, potencias, energias = melhor
    print("\n=== Melhor Solução Encontrada ===")
    for i in range(N_BATERIAS):
        print(f"Barra {barras[i]}: Potência = {potencias[i]:.2f} kW, Energia = {energias[i]:.2f} kWh")

    plt.plot(historico)
    plt.title("Convergência do Algoritmo Genético")
    plt.xlabel("Geração")
    plt.ylabel("Melhor Fitness")
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()