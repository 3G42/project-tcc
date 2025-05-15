
from itertools import combinations
import json
import sys

import pandas as pd
from src.simulation.program import pre_solve, programa
from src.analysis.iterative import iterative_search
from src.analysis.utils import drp_drc_define, print_data_simulation




def app_interface():
    print('Bem-vindo ao programa de busca analítica de melhor configuração para minimização de pertubações e perdas na rede.')
    
    while True:
        print('Por favor selecione uma opção')
        print('1 - Simulação sem GD e sem armazenamento - Caso inicial')
        print('2 - Simulação com GD e sem armazenamento')
        print('3 - Busca analitica de melhor configuração')
        print('4 - Sair')
        option = input('Selecione uma opção: ')
        
        
        match option:
            case '1':
                print('-----------------------------------------------------------------------------')
                print('--------- Simulação inicial do sistema - CASO 0 sem baterias e GDs ----------')
                print('-----------------------------------------------------------------------------')
                
                simulation_0 = programa(id_value='start_case', option='without-gd-storage')
                
                v_indicators_0 =  pd.DataFrame(**(json.loads(simulation_0['v_indicators'])))
                drp_0, drc_0 = drp_drc_define(v_indicators_0)
                feeder_energy_0 = simulation_0['feeder_energy']
                feeder_losses_0 = simulation_0['feeder_losses']
                
                print_data_simulation('0',drp_0,drc_0,feeder_energy_0,feeder_losses_0)
            
            case '2':
                print('-----------------------------------------------------------------------------')
                print('------------------------- Simulação com apenas GDs  -------------------------')
                print('-----------------------------------------------------------------------------')
                
                simulation_1 = programa(id_value='with_gd', option='with-gd-without-storage')
                v_indicators_1 = pd.DataFrame(**(json.loads(simulation_1['v_indicators'])))
                drp_1, drc_1 = drp_drc_define(v_indicators_1)
                feeder_energy_1 = simulation_1['feeder_energy']
                feeder_losses_1 = simulation_1['feeder_losses']
                
                print_data_simulation('1',drp_1,drc_1,feeder_energy_1,feeder_losses_1)
            
            case '3':
                print('-----------------------------------------------------------------------------')
                print('------------------------- Busca analitica de melhor configuração -------------')
                print('-----------------------------------------------------------------------------')
                
                max_bess = int(input('Informe o número máximo de BESS: \n'))
                total_power_bess = float(input('Informe a potência total de BESS(será distribuido igualmente entre os BESS): \n '))
                total_energy_bess = float(input('Informe a energia total de BESS: \n'))
                
                simulations = iterative_search(max_bess, total_power_bess, total_energy_bess)
    
            case '4':
                print('Saindo do programa...')
                sys.exit()
            
            case _:
                print('Opção inválida. Tente novamente.')
                continue
        

if __name__ == '__main__':
    
    app_interface()

        
    

    
    
    
    
    
