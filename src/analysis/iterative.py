from itertools import combinations
import os
import sys

import pandas as pd

caminho_absoluto = os.path.abspath(os.curdir) + '/src'
sys.path.insert(0, caminho_absoluto)

from analysis.utils import drp_drc_define
from simulation.program import programa,pre_solve


def execute_combination(simulation_id, buses, bess_power, bess_energy):
    storage_specs = [
        [f'{b}',bess_power,bess_energy] for b in buses 
    ]
    data = programa(id_value=simulation_id, option='with-gd-storage', storage_specs=storage_specs)
    drps, drcs = drp_drc_define(data['v_indicators'])
    drp=drps.max()
    drc=drcs.max()
    
    ignore = drp >= 3.0 or drc >= 0.5
    
    
    return data,drps,drcs,ignore



def iterative_search(max_bess=2, total_power_bess=100, total_energy_bess=200):
    simulations = {}
    dss = pre_solve()
    buses = dss.circuit.buses_names
    num_simulations = 1
    for num_bess in range(1, max_bess + 1):
        bess_power = total_power_bess / num_bess
        bess_energy = total_energy_bess / num_bess
        combs_buses = list(combinations(buses, num_bess))
        for b in combs_buses:
            data,drps,drcs,ignore = execute_combination(num_simulations, b, bess_power, bess_energy)
            if ignore==True:
                continue
            
            simulations[b] = {
                'simulation_id': num_simulations,
                'bess_power': bess_power,
                'bess_energy': bess_energy,
                'buses': b,
                'simulation': data,
                'drps':drps,
                'drcs':drcs
            }
            num_simulations = num_simulations + 1
    

        
        
   
    # for s in simulations:
    #     worst_drp = pd.Series(simulations[s]['drps']).max()
    #     worst_drc = pd.Series(simulations[s]['drcs']).max()
        
        # print('Simulação: ', s)
        # print('Potencia da bateria: ', simulations[s]['bess_power'])
        # print('Energia da bateria: ', simulations[s]['bess_energy'])
        # print('Barras: ', simulations[s]['buses'])
        # print('WORST DRP: ', worst_drp)
        # print('WORST DRC: ', worst_drc)
        # print('Feeder energy: ', simulations[s]['feeder_energy'])
        # print('Feeder losses: ', simulations[s]['feeder_losses'])
        # print('\n')
        
    #     if worst_drc <= best_drc:
    #         if worst_drc < best_drc:
    #             best_drc = worst_drc
    #             best_drp = worst_drp
    #             best_simulation = simulations[s]
    #             best_energy = simulations[s]['feeder_energy']
    #         else:
    #             if worst_drp <= best_drp:
    #                 if worst_drp < best_drp:
    #                     best_drp = worst_drp
    #                     best_simulation = simulations[s]
    #                     best_energy = simulations[s]['feeder_energy']
            

        
    return simulations
    # print('-----------------------------------------------------------------------------')
    # print('------------------------- Melhor  encontrada  --------------------')
    # print('-----------------------------------------------------------------------------')
    # print('Simulação: ', best_simulation['simulation_id'])
    # print('Potencia da bateria: ', best_simulation['bess_power'])
    # print('Energia da bateria: ', best_simulation['bess_energy'])
    # print('Barras: ', best_simulation['buses'])
    # print('DRP: ', pd.Series(best_simulation['drp']).max())
    # print('DRC: ', pd.Series(best_simulation['drc']).max())
    # print('Feeder energy: ', best_simulation['feeder_energy'])
    # print('Feeder losses: ', best_simulation['feeder_losses'])
    
    # return best_simulation
        
if __name__ == "__main__":
    
    teste = iterative_search(3, 30, 120)
    
    print('')
    
