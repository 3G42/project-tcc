import random

from src.simulation._old.Circuito_classes import pre_algorithm
from src.simulation.program import programa
from src.simulation.utils import drp_drc_define

start_case_data = programa()
rede, barras = pre_algorithm()

### Como potência máxima do alimentador é 75KVA potência instalada das baterias não pode exceder 2 x 75KW

potencia_maxima = 150.0
## Barra e conexões do primário do trafo removida
barras.pop(00)
rede.pop(00)

### Parametros do algoritmo

n_baterias = int(input("Informe o número de baterias"))
pot_por_bateria = int(input("Informe a potência que bateria terá"))
n_geracoes = 50
n_individuos = 10
Xcross = 0.6    # taxa de cruzamento
Xmut = 0.25

ind_hist = []


def avalia_ind(ind,battery_power):
    storage_specs = []
    for b in ind:

        barra = b
        pot = battery_power
        energia = 2 * battery_power
        storage_specs.append([barra, pot, energia])

    resultado = programa(option="with-gd-storage", storage_specs=storage_specs)

    indicadores = resultado['v_indicators']
    ind_hist.append(resultado['pa'].copy())
    feeder_losses = resultado['feeder_losses']
    feeder_power = resultado['feeder_energy']
    drps, drcs = drp_drc_define(indicadores)
    drp = drps.mean()
    drc = drcs.mean()

    fitness = 20*drc + 5*drp # penalização aumentada
    return fitness

def avalia_populacao(population,batery_power):
    fit_pop = {}

    for k,v in population.items():
        fit_pop[k] = avalia_ind(v,batery_power)

    return fit_pop


def cruzamento(ind1, ind2):
    n = len(ind1)
    ponto_corte = random.randint(1, n - 2)

    filho1 = ind1[:ponto_corte] + [g for g in ind2 if g not in ind1[:ponto_corte]]
    filho2 = ind2[:ponto_corte] + [g for g in ind1 if g not in ind2[:ponto_corte]]

    return sorted(filho1), sorted(filho2)

def selecao(populacao, fitnesses):
    # Seleção aleatória de dois indivíduos (sem roleta)
    return random.sample(populacao, 2)

def cruzamento(pai1, pai2):
    if random.random() < Xcross:
        k = random.randint(1, n_baterias - 1)
        filho1 = pai1[:k] + pai2[k:]
        filho2 = pai2[:k] + pai1[k:]
        return [filho1, filho2]
    return [pai1[:], pai2[:]]

def mutacao(individuo):
    if random.random() < Xmut:
        m = random.randint(0, n_baterias - 1)
        # Lista de barras disponíveis, excluindo as já presentes no indivíduo
        barras_disponiveis = list(set(barras.keys()) - set(individuo))
        if barras_disponiveis:
            novo_valor = random.choice(barras_disponiveis)
            individuo[m] = novo_valor
    return individuo


### Gerar individuos iniciais.
### Modelo de cada Individuo
### para n_baterias = 3 -> [barra1, barra2, barra3]
individuos = {}
for i in range(n_individuos):
    print('individuo: ', i)
    while True:
        indiv = sorted(random.sample(sorted(barras.keys()),n_baterias))
        if not(indiv in list(individuos.values())):
            break

    individuos[i] = indiv


for gen in range(n_geracoes):
    print(f"\n>>> Geração {gen+1}")
    fit_pop = avalia_populacao(individuos, pot_por_bateria)

    # Ordena os indivíduos por fitness crescente (melhores primeiro)
    ind_fit = [(individuos[idx], fit_pop[idx]) for idx in list(individuos.keys())]
    ind_fit = sorted(ind_fit, key=lambda x: x[1])
    nova_populacao = {}

    # 1. Elitismo: mantém os dois melhores indivíduos diretamente
    nova_populacao[0] = ind_fit[0][1]  # melhor
    nova_populacao[1] = ind_fit[1][1]  # segundo melhor

    # 2. Crossover entre os dois melhores
    filhos = cruzamento(ind_fit[0][1], ind_fit[1][1])
    nova_populacao[2] = filhos[0]
    if len(nova_populacao) < n_individuos:
        nova_populacao[3] = filhos[1]

    # 3. Mutação dos piores (restante da população)
    count = len(nova_populacao)
    for idx in range(n_individuos - 1, 1, -1):  # começa dos piores
        if count >= n_individuos:
            break
        mutante = mutacao(ind_fit[idx][1][:])  # faz cópia antes de mutar
        nova_populacao[count] = mutante
        count += 1

    individuos = nova_populacao

    # Print de resultado da geração
    best_fitness = fit_pop[ind_fit[0][0]]
    print(f"Melhor fitness: {best_fitness}")
    print(f"Melhor solução: {ind_fit[0][1]}")