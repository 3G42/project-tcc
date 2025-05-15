import numpy as np

from simulation.program import programa



def avaliar_bess(power_storage, energy_storage, position_storage):
    """
    Evaluates the BESS cost function.

    Parameters:
    - params: List of parameters to evaluate.

    Returns:
    - Cost value.
    """
    results = programa(id_value='otimizacao', option='with-gd-without-storage', storage_specs=[[position_storage,power_storage,energy_storage]])    
    
    v_indicators = results['v_indicators']
    drp_values = v_indicators.loc[['DRP_A', 'DRP_B', 'DRP_C']]
    ### Selecione os maiores valores de cada coluna
    drp_values = drp_values.max(axis=0)
    ### Conta a quantidade de valores maior ou igual a 3
    drp_count = (drp_values >= 3).sum()
    
    
    ### Selecione os maiores valores de cada coluna    
    ## Calcular uma métrica de perda de energia

    
    losses_percentual =  (results['feeder_losses']/results['feeder_energy'])*100
    
    print(losses_percentual)
    
    custo = drp_count*1000 + losses_percentual*10
    
    print(f'Quantidade de DRP: {drp_count}')
    print(f'Perdas: {losses_percentual}')
    print(f'Custo: {custo}')
    
    return custo,drp_count,losses_percentual
    
if __name__ == "__main__":
    # Example usage
    
    avaliar_bess()