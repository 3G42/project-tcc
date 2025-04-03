import random

import numpy as np

from src.simulation.Particle import Particle
from src.simulation.genetic_optimizer import start_case


class Swarm:
    def __init__ (self,particles:list[Particle]):
        """Inicializa o enxame com uma lista de partículas.
        particles: lista de objetos Particle
        """
        self.particles = particles

    @staticmethod
    def gerar_binario_baterias(num_barras, max_baterias):
        qtd_baterias = random.randint(1, max_baterias)
        print(qtd_baterias)
        posicoes = random.sample(range(1,num_barras), qtd_baterias)
        binario = [1 if i in posicoes else 0 for i in range(num_barras)]
        return binario, qtd_baterias


    @staticmethod
    def distribuir_potencia_aleatoria(total, n):
        if n == 0:
            return []

        pesos = np.random.dirichlet(np.ones(n))
        potencias = [int(peso * total) for peso in pesos]
        potencias = [1 if p == 0 else p for p in potencias]
        soma = sum(potencias)
        ajuste = total - sum(potencias)
        i = 0
        while ajuste != 0:
            if ajuste > 0:
                potencias[i] += 1
                ajuste -= 1
            elif ajuste < 0 and potencias[i] > 0:
                potencias[i] -= 1
                ajuste += 1
            i = (i + 1) % n

        return potencias

    @staticmethod
    def gerar_particula(num_barras, max_baterias, pot_total_min, pot_total_max, min_const, max_const):
        pot_total = random.randint(pot_total_min, pot_total_max)
        binario, qtd_baterias = Swarm.gerar_binario_baterias(num_barras, max_baterias)
        if qtd_baterias == 0:
            potencias = [0] * num_barras
        else:
            # Distribui potências aleatórias, mantendo soma = pot_total_max
            pot_aleatorias = Swarm.distribuir_potencia_aleatoria(pot_total, qtd_baterias)
            potencias = []
            idx_pot = 0
            for b in binario:
                if b == 1:
                    potencias.append(pot_aleatorias[idx_pot])
                    idx_pot += 1
                else:
                    potencias.append(0)

        constante_energia = random.randint(min_const, max_const)
        part = Particle(potencias, constante_energia,False,pot_total)
        return part

    @staticmethod
    def gerar_potencia_aleatorias(num_barras, min_pot, max_pot):
        """Gera uma lista de potências aleatórias para as barras."""
        return [random.randint(min_pot, max_pot) for _ in range(num_barras)]

    @classmethod
    def gerar_enxame_aleatorio(cls, num_particulas, num_barras, max_baterias, pot_total_max, min_const, max_const):
        particles = [
            cls.gerar_particula(num_barras, max_baterias,2, pot_total_max, min_const, max_const)
            for _ in range(num_particulas)
        ]
        return cls(particles)