import pandas as pd


def drp_drc_define(v_indicators: pd.DataFrame):
    drps = v_indicators.loc[['DRP_A', 'DRP_B', 'DRP_C']]
    drcs = v_indicators.loc[['DRC_A', 'DRC_B', 'DRC_C']]
    drp_per_bus = drps.sum(axis=0)
    drc_per_bus = drcs.sum(axis=0)
    
    return drp_per_bus, drc_per_bus


def print_data_simulation(name,drp,drc,feeder_energy,feeder_losses):
    print('\n')
    print('----- Resultados da simulação {}  --------'.format(name))
    print('\n')
    print('- DRP por barramento: \n', drp,' \n')
    print('- DRC por barramento: \n', drc,' \n')
    print('- Energia total do sistema: \n', feeder_energy,'\n')
    print('- Perdas totais do sistema: \n', feeder_losses,'\n')
    print('\n')
    

