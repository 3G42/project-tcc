import random
import numpy as np
from deap import base, creator, tools, algorithms
from program import programa  # importa sua simulação
import pandas as pd


def drp_drc_define(v_indicators: pd.DataFrame):
    drps = v_indicators.loc[['DRP_A', 'DRP_B', 'DRP_C']]
    drcs = v_indicators.loc[['DRC_A', 'DRC_B', 'DRC_C']]
    drp_per_bus = drps.max(axis=0)
    drc_per_bus = drcs.max(axis=0)
    
    return drp_per_bus, drc_per_bus

NUM_BESS = 3
POT_MIN = 10
POT_MAX = 500
BARRAS_CANDIDATAS = list(range(2, 15))

# === Configuração do GA ===



class BESS:
    def __init__(self, barra, potencia, energia):
        if barra not in BARRAS_CANDIDATAS:
            raise ValueError(f"Barra {barra} não é válida. Deve ser uma das {BARRAS_CANDIDATAS}.")
        if potencia == 0:
            raise ValueError("Potência não pode ser zero.")
        if energia == 0:
            raise ValueError("Energia não pode ser zero.")
        self._barra = barra
        self._potencia = potencia
        self._energia = energia
    
    def __repr__(self):
        return f"BESS(Barra: {self._barra}, Potência: {self._potencia}, Energia: {self._energia})"
    def to_list(self):
        return [self._barra, self._potencia, self._energia]
    
    
class Individuo:
    def __init__(self, n_bess=NUM_BESS,pot_min=POT_MIN, pot_max=POT_MAX):
        self._bess_list = []
        self._n_bess = n_bess
        self._max_pot_of_bess = POT_MAX/n_bess
        if self._max_pot_of_bess < pot_min:
            self._min_pot_of_bess = pot_min
            self._max_pot_of_bess = pot_min
        self._max_energy_of_bess = POT_MAX*3/n_bess
        
        self._pot_max = pot_max
        for _ in range(self._n_bess):
            self.create_bess()
        
            
        
    def create_bess(self):
        barra = random.choice(BARRAS_CANDIDATAS)
        # Garante que a barra não seja repetida
        while any(b._barra == barra for b in self._bess_list):
            barra = random.choice(BARRAS_CANDIDATAS)
        pot = random.uniform(POT_MIN, self._max_pot_of_bess)
        energia = random.uniform(POT_MIN*3, self._max_energy_of_bess)
        bess = BESS(barra, pot, energia)
        self._bess_list.append(bess)
    
    def to_list(self):
        list_of_bess =  [b.to_list() for b in self._bess_list]
        while len(list_of_bess) < NUM_BESS:
            list_of_bess.append([0, 0, 0])  # Preenche com BESSs vazios
        
        return list_of_bess
        


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)



def cria_individuo():
    
    num_of_bess = random.randint(1, NUM_BESS)
    print(f"Gerando indivíduo com {num_of_bess} BESSs.")
    individuo = Individuo(n_bess=num_of_bess)    
    return creator.Individual(individuo.to_list())

def barra_vizinha_livre(barra_atual, barras_candidatas, barras_usadas):
    # Procura primeiro para cima, depois para baixo
    distancias = sorted(set(barras_candidatas) - barras_usadas, key=lambda x: abs(x - barra_atual))
    if distancias:
        return distancias[0]
    return None

def sanitizar_individuo(individuo, barras_candidatas, pot_min, pot_max, num_bess):
    barras_vistas = set()
    max_pot_of_bess = pot_max / num_bess
    max_energy_of_bess = pot_max * 3 / num_bess

    for bess in individuo:
        barra, pot, energia = bess

        if barra == 0:
            bess[0], bess[1], bess[2] = 0, 0, 0
            continue

        if barra not in barras_candidatas or barra in barras_vistas:
            nova_barra = barra_vizinha_livre(barra, barras_candidatas, barras_vistas)
            if nova_barra is not None:
                bess[0] = nova_barra
                barra = nova_barra
            else:
                bess[0], bess[1], bess[2] = 0, 0, 0
                continue

        barras_vistas.add(barra)
        bess[1] = float(np.clip(pot, pot_min, max_pot_of_bess))
        bess[2] = float(np.clip(energia, pot_min * 3, max_energy_of_bess))
        if bess[1] <= 0 or bess[2] <= 0:
            bess[0], bess[1], bess[2] = 0, 0, 0

    return individuo

start_case = programa( option="without-gd-storage")
drps_start_case,drcs_start_case = drp_drc_define(start_case['v_indicators'])
max_drp_start = drps_start_case.max()
max_drc_start = drcs_start_case.max()

toolbox = base.Toolbox()
toolbox.register("individual", cria_individuo)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def avaliar(individuo):
    # Força a barra a ser inteira e válida
    storage_specs = []
    for bess in individuo:
        
        barra = bess[0]
        if barra not in BARRAS_CANDIDATAS:
            continue
        pot = bess[1]
        energia = bess[2]
        storage_specs.append([barra, pot, energia])

    resultado = programa(option="with-gd-storage", storage_specs=storage_specs)


    indicadores = resultado['v_indicators']
    feeder_losses = resultado['feeder_losses']
    drps, drcs = drp_drc_define(indicadores)
    drps = np.maximum(drps - drps_start_case, 0)
    drcs = np.maximum(drcs - drcs_start_case, 0)
    drp = drps.max()
    drc = drcs.max()
    
    # Verifica exportação de energia (fluxo reverso)

    fitness = drcs.sum() * 20 + drps.sum() * 10  # penalização aumentada
    print(f"Indivíduo: {individuo}, \n FeederLosses: {feeder_losses}\n Fitness: {fitness}")
    return (fitness,)


toolbox.register("evaluate", avaliar)



def crossover_sanitizado(ind1, ind2):
    i1, i2 = tools.cxTwoPoint(ind1, ind2)
    i1 = sanitizar_individuo(i1, BARRAS_CANDIDATAS, POT_MIN, POT_MAX, NUM_BESS)
    i2 = sanitizar_individuo(i2, BARRAS_CANDIDATAS, POT_MIN, POT_MAX, NUM_BESS)
    return i1, i2

toolbox.register("mate", crossover_sanitizado)


def mutacao_customizada(individuo, indpb=0.3):
    # individuo: [[barra, pot, energia], ...] (até NUM_BESS elementos)
    for bess in individuo:
        # Só muta se for um BESS válido (barra diferente de 0)
        if bess[0] in BARRAS_CANDIDATAS:
            # Mutação da barra
            if random.random() < indpb:
                barras_possiveis = [b for b in BARRAS_CANDIDATAS if b != bess[0]]
                bess[0] = random.choice(barras_possiveis)
            # Mutação da potência
            if random.random() < indpb:
                max_pot_of_bess = POT_MAX / NUM_BESS
                bess[1] = float(np.clip(bess[1] + random.gauss(0, 15), POT_MIN, max_pot_of_bess))
            # Mutação da energia
            if random.random() < indpb:
                max_energy_of_bess = POT_MAX * 3 / NUM_BESS
                bess[2] = float(np.clip(bess[2] + random.gauss(0, 30), POT_MIN * 3, max_energy_of_bess))
                
    # Sanitiza o indivíduo após a mutação
    individuo = sanitizar_individuo(individuo, BARRAS_CANDIDATAS, POT_MIN, POT_MAX, NUM_BESS)

    
    return (individuo,)


toolbox.register("mutate", mutacao_customizada)
toolbox.register("select", tools.selBest)

def eaSimpleElitism(population, toolbox, cxpb, mutpb, ngen, stats=None, halloffame=None, verbose=__debug__):
    for gen in range(ngen):
        offspring = toolbox.select(population, len(population) - (len(halloffame) if halloffame else 1))
        offspring = list(map(toolbox.clone, offspring))

        # Cruzamento e mutação
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Avaliação dos indivíduos com fitness inválido
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Elitismo moderado: mantém os melhores do HallOfFame
        if halloffame is not None:
            halloffame.update(population)
            elites = [toolbox.clone(ind) for ind in halloffame]
            for elite in elites:
                if not elite.fitness.valid:
                    elite.fitness.values = toolbox.evaluate(elite)
                offspring.append(elite)

        population[:] = offspring

        if stats:
            record = stats.compile(population)
            if verbose:
                print(record)
    return population


# === Execução ===
def rodar_ga(geracoes=20, tamanho_pop=100):
    pop = toolbox.population(n=tamanho_pop)
    hof = tools.HallOfFame(2)  # Mantém os 2 melhores
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("min", np.min)

    pop = eaSimpleElitism(pop, toolbox, cxpb=0.5, mutpb=0.3, ngen=geracoes,
                          stats=stats, halloffame=hof, verbose=True)

    print("\nMelhor solução:")
    melhor = hof[0]
    print("Indivíduo:", melhor)
    print("Fitness:", melhor.fitness.values[0])
    return melhor

if __name__ == "__main__":
    
    
    

    
    melhor = rodar_ga(geracoes=50, tamanho_pop=20)
    print("Melhor indivíduo encontrado:", melhor)

    storage_specs = []
    for bess in melhor:

        barra = bess[0]
        if barra not in BARRAS_CANDIDATAS:
            continue
        pot = bess[1]
        energia = bess[2]
        storage_specs.append([barra, pot, energia])
    resultado = programa(option="with-gd-storage", storage_specs=storage_specs)

    import matplotlib.pyplot as plt
    import math

    # Limites em pu
    faixa_precaria_inf_min = 0.866
    faixa_precaria_inf_max = 0.921
    faixa_precaria_sup_min = 1.047
    faixa_precaria_sup_max = 1.063
    faixa_critica_inf = 0.866
    faixa_critica_sup = 1.063

    va = resultado["va"]
    vb = resultado["vb"]
    vc = resultado["vc"]
    resultado_gd_sem_storage = programa(option="without-gd-storage")

    va_gd = resultado_gd_sem_storage["va"]
    vb_gd = resultado_gd_sem_storage["vb"]
    vc_gd = resultado_gd_sem_storage["vc"]

    # 2. Simulação para o melhor indivíduo já está em va, vb, vc

    barras = list(va.columns)
    n_barras = len(barras)
    n_janelas = 4
    barras_por_janela = math.ceil(n_barras / n_janelas)
    grupos = [barras[i * barras_por_janela:(i + 1) * barras_por_janela] for i in range(n_janelas)]

    for i, grupo in enumerate(grupos):
        ncols = 3
        nrows = math.ceil(len(grupo) / ncols)
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 4 * nrows), sharex=True, sharey=True)
        fig.suptitle(f'Grupo {i + 1}', fontsize=16)
        axes = np.array(axes).flatten()
        for idx, barra in enumerate(grupo):
            axes[idx].plot(va.index, va[barra], label='Va (Otimizado)', color='b')
            axes[idx].plot(vb.index, vb[barra], label='Vb (Otimizado)', color='g')
            axes[idx].plot(vc.index, vc[barra], label='Vc (Otimizado)', color='r')
            axes[idx].plot(va_gd.index, va_gd[barra], '--', label='Va (GD s/ Storage)', color='b', alpha=0.5)
            axes[idx].plot(vb_gd.index, vb_gd[barra], '--', label='Vb (GD s/ Storage)', color='g', alpha=0.5)
            axes[idx].plot(vc_gd.index, vc_gd[barra], '--', label='Vc (GD s/ Storage)', color='r', alpha=0.5)
            axes[idx].set_title(f'Barra {barra}')
            axes[idx].set_xlabel('Hora')
            axes[idx].set_ylabel('Tensão (pu)')
            axes[idx].grid(True)
            # Linhas das faixas
            axes[idx].axhline(0.866, color='orange', linestyle='--', linewidth=1, label='Precária/Crítica')
            axes[idx].axhline(0.921, color='orange', linestyle='--', linewidth=1)
            axes[idx].axhline(1.047, color='orange', linestyle='--', linewidth=1)
            axes[idx].axhline(1.063, color='orange', linestyle='--', linewidth=1)
            axes[idx].axhline(0.866, color='red', linestyle=':', linewidth=1, label='Crítica')
            axes[idx].axhline(1.063, color='red', linestyle=':', linewidth=1)
            handles, labels = axes[idx].get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            axes[idx].legend(by_label.values(), by_label.keys())
        # Remove subplots vazios
        for j in range(len(grupo), len(axes)):
            fig.delaxes(axes[j])
        plt.tight_layout()
        plt.show()
