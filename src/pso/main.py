from simulation.program import programa


def main():
    resultados_simulacao = programa(1)
    print(resultados_simulacao)
    avaliar_bess(resultados_simulacao)

if __name__ == "__main__":
    main()