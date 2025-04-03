import copy
import random

import numpy as np
from matplotlib import pyplot as plt

from src.simulation.Particle import Particle
from src.simulation.Swarm import Swarm


class PSO:
    def __init__(self, num_particulas, num_barras, max_baterias, pot_total_max, min_const, max_const, limiar_potencia, max_iteracoes):
        self.num_barras = num_barras
        self.max_baterias = max_baterias
        self.pot_total_max = pot_total_max
        self.limiar_potencia = limiar_potencia
        self.max_iteracoes = max_iteracoes

        self.swarm = Swarm.gerar_enxame_aleatorio(
            num_particulas, num_barras, max_baterias, pot_total_max, min_const, max_const
        )

        self.p_best = [copy.deepcopy(p) for p in self.swarm.particles]
        self.p_best_scores = [float("inf")] * num_particulas
        self.g_best = None
        self.g_best_score = float("inf")

        self.start_case = None
        self.start_case_score = float("inf")

        self.historico_scores = []

    def avaliar_fitness(self, part: Particle, is_start=False):
        if part.drps is None or part.drcs is None:
            part.simular()

        if is_start:
            return 20 * part.drcs.sum() + 5 * part.drps.sum()



        # Penalidades principais
        penalidade_drc = part.drcs.sum()  # mais importante
        penalidade_drp = part.drps.sum()  # secundário

        # Penalidade extra por número de barras ainda com violação
        violacoes_drc = np.count_nonzero(part.drcs > 0.01)
        violacoes_drp = np.count_nonzero(part.drps > 0.01)

        # Penalização por potência excessiva (acima do ideal)
        ideal_pot = 50
        excesso = max(0, part.pot_total - ideal_pot)
        penalidade_pot = (excesso / 5) ** 2  # penaliza suavemente

        fitness = (
                20 * penalidade_drc +
                5 * penalidade_drp +
                30 * (violacoes_drc + violacoes_drp) +
                10 * penalidade_pot
        )
        return fitness

    def mover_particula(self, part: Particle, pbest: Particle, gbest: Particle):
        nova_part = copy.deepcopy(part)
        barras_atual = [i for i, p in enumerate(part.potencias) if p > 0]
        barras_pbest = [i for i, p in enumerate(pbest.potencias) if p > 0]
        barras_gbest = [i for i, p in enumerate(gbest.potencias) if p > 0]

        if not barras_atual:
            return part

        for _ in range(3):  # tenta até 3 vezes
            barra_substituir = random.choice(barras_atual)
            if random.random() < 0.5 and barras_pbest:
                nova_barra = random.choice(barras_pbest)
            elif barras_gbest:
                nova_barra = random.choice(barras_gbest)
            else:
                continue

            if nova_barra not in barras_atual:
                nova_part.potencias[barra_substituir] = 0
                nova_part.potencias[nova_barra] = part.pot_total / len(barras_atual)
                nova_part.arredondar_potencias()
                nova_part.simular()
                return nova_part

        # Se nenhuma mutação válida ocorreu, recriação parcial
        nova_part = Swarm.gerar_particula(
            self.num_barras,
            self.max_baterias,
            part.pot_total,  # mantém a mesma potência total
            part.pot_total,
            part.constante_energia,
            part.constante_energia
        )
        return nova_part

    def executar(self):
        pot_zero = [0] * self.num_barras
        self.start_case = Particle(pot_zero, 1)
        self.start_case.simular()
        self.start_case_score = self.avaliar_fitness(self.start_case, is_start=True)
        print("SCORE START CASE", self.start_case_score)

        for iteracao in range(self.max_iteracoes):
            print(f"Iteração {iteracao+1}/{self.max_iteracoes}")
            for i, part in enumerate(self.swarm.particles):
                score = self.avaliar_fitness(part)

                if score < self.p_best_scores[i]:
                    self.p_best_scores[i] = score
                    self.p_best[i] = copy.deepcopy(part)

                if score < self.g_best_score:
                    self.g_best_score = score
                    self.g_best = copy.deepcopy(part)

            num_baterias = sum(1 for p in self.g_best.potencias if p > 0)
            print(f"Gbest: {self.g_best.storage_specs}  SCORE: {self.g_best_score}  BATERIAS: {num_baterias}")

            self.swarm.particles = [
                self.mover_particula(part, self.p_best[i], self.g_best)
                for i, part in enumerate(self.swarm.particles)
            ]
            self.historico_scores.append(self.g_best_score)

        print("PSO finalizado.")
        print("Melhor solução encontrada:")
        print(self.g_best.get_storage_specs(self.limiar_potencia))
        print(f"Score: {self.g_best_score}")


if __name__ == "__main__":
    grafo_rede = 
    pso = PSO(
        num_particulas=20,
        num_barras=15,
        max_baterias=10,
        pot_total_max=200,
        min_const=1,
        max_const=2,
        limiar_potencia=5,
        max_iteracoes=20
    )

    pso.executar()

    plt.plot(pso.historico_scores, marker='o')
    plt.title("Evolução do Fitness (gBest)")
    plt.xlabel("Iteração")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.show()