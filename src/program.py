# %% [markdown]
# # TCC
# 
# 

# %% [markdown]
# 
# ### 1. Introdução

# %% [markdown]
# ##### Importando libs

# %%
import datetime
import numpy as np
import pandas as pd
import py_dss_interface as pydss
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def str_to_time(string:str):
    return datetime.datetime.strptime(string,'%H:%M')

# %% [markdown]
# ##### Instanciando py-dss

# %%
dssObj = pydss.DSS()
project_file = r"C:/Users/gabri/project-tcc/src/circbtfull_storage.dss"
dssObj.text(f"compile {project_file}")

# %% [markdown]
# ##### Coletando itens da aplicação

# %%
nodes_names = dssObj.circuit.nodes_names
elements_names = dssObj.circuit.elements_names
buses_names=dssObj.circuit.buses_names
num_buses = dssObj.circuit.num_buses
num_cktelement = dssObj.circuit.num_ckt_elements

# %% [markdown]
# ### 2. Simulação de caso inicial
#     Nesta primeira etapa iremos analisar o circuito BT sem a presença de geradores fotovoltaicos, bem como de sistemas de armazenamento de energia

# %%

for element in elements_names:
    dssObj.circuit.set_active_element(element)
    if not (element.find("Generator.") == -1  and element.find("Storage.") == -1):
        if dssObj.cktelement.is_enabled == 1:
            dssObj.cktelement.enabled(0)






# %%
step_size_min = 15
step_size_sec = 60*step_size_min # SEGUNDOS
total_time_hour = 24 # hours
total_simulations = int(total_time_hour * 60 / step_size_min)


dssObj.solution.mode = 1
dssObj.solution.step_size = step_size_sec ## ESTE VALOR DETERMINA O STEP_SIZE EM SEGUNDOS
dssObj.solution.number = 1 ## ESTE DETERMINA QUANTAS VEZES É EXECTUADO O PASSO NA SIMULAÇÃO. DEVE FICAR EM 1. O AJUSTE É FEITO NO STEP SIZE


# %% [markdown]
# Coletaremos a curva de tensão, e de potência de cada barra do circuito 

# %%
header = pd.date_range('00:00:00', periods=total_simulations, freq=f'{step_size_min}min').strftime('%H:%M')
df = pd.DataFrame(index=nodes_names,columns=header)

for h in range(total_simulations):
    instant = datetime.time(hour=dssObj.solution.hour,minute=int(dssObj.solution.seconds // 60)).strftime('%H:%M')
    dssObj.solution.solve()
    
    bus_voltages = dssObj.circuit.buses_volts
    df[instant] = [
        (bus_voltages[j] + 1j * bus_voltages[j+1]) for j in range(0,len(bus_voltages),2)
    ]

df['Bus'] = [
    n.split('.')[0] for n in df.index
]
df['Phase'] = [
    n.split('.')[1] for n in df.index
]   


# %%
grouped = df.groupby('Bus')
rows_subplot = len(df['Bus'].unique())//2 if len(df['Bus'].unique())%2 == 0 else len(df['Bus'].unique())//2 + 1

# %%
for bus,group in grouped:
    group_transposed = group.T
    group_transposed.columns = [f"Voltage_{p}" for p in group_transposed.loc['Phase']]
    group_transposed = group_transposed.drop(index=['Bus','Phase'])
    if 'Voltage_4' in group_transposed.columns:
        group_transposed = group_transposed.drop(columns="Voltage_4")
    group_transposed = group_transposed.map(abs)
    group_transposed.index = group_transposed.index.map(str_to_time)
    plt.figure()
    
    for column in group_transposed.columns:
        plt.plot(group_transposed.index, group_transposed[column], label=column)
    
    plt.title(f'Tensão em função do horário para a barra {bus}')
    plt.xlabel('Horário')
    plt.ylabel('Tensão (V)')
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'voltage_plot_{bus}.png')  # Salvando o gráfico como imagem


# %%
for element in elements_names:
    dssObj.circuit.set_active_element(element)
    if not (element.find("Generator.") == -1):
        if dssObj.cktelement.is_enabled == 0:
            dssObj.cktelement.enabled(1)

dssObj.solution.dbl_hour = 0.0
            

# %%
header = pd.date_range('00:00:00', periods=total_simulations, freq=f'{step_size_min}min').strftime('%H:%M')
df_new = pd.DataFrame(index=nodes_names,columns=header)

for h in range(total_simulations):
    instant = datetime.time(hour=dssObj.solution.hour,minute=int(dssObj.solution.seconds // 60)).strftime('%H:%M')
    dssObj.solution.solve()
    
    bus_voltages = dssObj.circuit.buses_volts
    df_new[instant] = [
        (bus_voltages[j] + 1j * bus_voltages[j+1]) for j in range(0,len(bus_voltages),2)
    ]

    


# %%
df_new['Bus'] = [
    n.split('.')[0] for n in df_new.index
]
df_new['Phase'] = [
    n.split('.')[1] for n in df_new.index
]

grouped_new = df_new.groupby('Bus')
rows_subplot = len(df_new['Bus'].unique())//2 if len(df_new['Bus'].unique())%2 == 0 else len(df_new['Bus'].unique())//2 + 1

# %%
for bus,group in grouped_new:
    group_transposed = group.T
    group_transposed.columns = [f"Voltage_{p}" for p in group_transposed.loc['Phase']]
    group_transposed = group_transposed.drop(index=['Bus','Phase'])
    if 'Voltage_4' in group_transposed.columns:
        group_transposed = group_transposed.drop(columns="Voltage_4")
    group_transposed = group_transposed.map(abs)
    group_transposed.index = group_transposed.index.map(str_to_time)
    plt.figure()
    
    for column in group_transposed.columns:
        plt.plot(group_transposed.index, group_transposed[column], label=column)
    
    plt.title(f'Tensão em função do horário para a barra {bus}')
    plt.xlabel('Horário')
    plt.ylabel('Tensão (V)')
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'voltage_plot_{bus}.png')  # Salvando o gráfico como imagem


# %%

