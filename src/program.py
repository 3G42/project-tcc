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
import math
import os
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


## Instanciando o DSS
dss = pydss.DSS()
# dss.dssinterface.allow_forms = False

project_file = os.path.join(os.path.dirname(__file__),"circbtfull_storage.dss")


dss.text(f"Compile {project_file}")
dss.text('Set mode=daily')
dss.text("Set stepsize=1h")
dss.text("Set number=24")



### Nome de elementos principais do circuito
buses = dss.circuit.buses_names
nodes = dss.circuit.nodes_names
elements = dss.circuit.elements_names
transformers = dss.transformers.names  
lines = dss.lines.names

for l in lines:
    print(l)
    dss.text(f"New Monitor.V_{l}_T1 element=Line.{l} terminal=1 mode=0 ")
    dss.text(f"New Monitor.V_{l}_T2 element=Line.{l} terminal=2 mode=0 ")


for t in transformers:
    dss.text(f"New Monitor.P_{t} element=Transformer.{t} terminal=1 mode=1 ppolar=no")



monitors = dss.monitors.names





###############################################################
### Simulando para o estado inicial: Sem GD e Armazenamento ###
###############################################################

#Desativando as baterias
for element in elements:
    dss.circuit.set_active_element(element)
    if not (element.find("Generator.") == -1  and element.find("Storage.") == -1):
        if dss.cktelement.is_enabled == 1:
            dss.cktelement.enabled(0)
            
            
dss.solution.solve()        

    
va_df = pd.DataFrame(np.zeros((24,len(monitors)-1)))
vb_df = pd.DataFrame(np.zeros((24,len(monitors)-1)))
vc_df = pd.DataFrame(np.zeros((24,len(monitors)-1)))
va_df.columns = monitors[0:len(monitors)-1]
vb_df.columns = monitors[0:len(monitors)-1]
vc_df.columns = monitors[0:len(monitors)-1]

dss.monitors.first()
for _ in monitors:
    if _!='p_trafo': 
        va_df[_] = dss.monitors.channel(1)
        vb_df[_] = dss.monitors.channel(3)
        vc_df[_] = dss.monitors.channel(5)
    
    dss.monitors.name = _
    

# va_df = va_df.div((127/math.sqrt(3)))

print(va_df)
print(vb_df)
print(vc_df)



# # %%
# step_size_min = 15
# step_size_sec = 60*step_size_min # SEGUNDOS
# total_time_hour = 24 # hours
# total_simulations = int(total_time_hour * 60 / step_size_min)


# ## ESTE DETERMINA QUANTAS VEZES É EXECTUADO O PASSO NA SIMULAÇÃO. DEVE FICAR EM 1. O AJUSTE É FEITO NO STEP SIZE


# # %% [markdown]
# # Coletaremos a curva de tensão, e de potência de cada barra do circuito 

# # %%
# header = pd.date_range('00:00:00', periods=total_simulations, freq=f'{step_size_min}min').strftime('%H:%M')
# df = pd.DataFrame(index=nodes_names,columns=header)

# for h in range(total_simulations):
#     instant = datetime.time(hour=dss.solution.hour,minute=int(dss.solution.seconds // 60)).strftime('%H:%M')
#     dss.solution.solve()
    
#     bus_voltages = dss.circuit.buses_volts
#     df[instant] = [
#         (bus_voltages[j] + 1j * bus_voltages[j+1]) for j in range(0,len(bus_voltages),2)
#     ]

# df['Bus'] = [
#     n.split('.')[0] for n in df.index
# ]
# df['Phase'] = [
#     n.split('.')[1] for n in df.index
# ]   


# # %%
# grouped = df.groupby('Bus')
# rows_subplot = len(df['Bus'].unique())//2 if len(df['Bus'].unique())%2 == 0 else len(df['Bus'].unique())//2 + 1

# # %%
# for bus,group in grouped:
#     group_transposed = group.T
#     group_transposed.columns = [f"Voltage_{p}" for p in group_transposed.loc['Phase']]
#     group_transposed = group_transposed.drop(index=['Bus','Phase'])
#     if 'Voltage_4' in group_transposed.columns:
#         group_transposed = group_transposed.drop(columns="Voltage_4")
#     group_transposed = group_transposed.map(abs)
#     group_transposed.index = group_transposed.index.map(str_to_time)
#     plt.figure()
    
#     for column in group_transposed.columns:
#         plt.plot(group_transposed.index, group_transposed[column], label=column)
    
#     plt.title(f'Tensão em função do horário para a barra {bus}')
#     plt.xlabel('Horário')
#     plt.ylabel('Tensão (V)')
#     plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#     plt.xticks(rotation=45)
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(f'voltage_plot_{bus}.png')  # Salvando o gráfico como imagem


# # %%
# for element in elements_names:
#     dss.circuit.set_active_element(element)
#     if not (element.find("Generator.") == -1):
#         if dss.cktelement.is_enabled == 0:
#             dss.cktelement.enabled(1)

# dss.solution.dbl_hour = 0.0
            

# # %%
# header = pd.date_range('00:00:00', periods=total_simulations, freq=f'{step_size_min}min').strftime('%H:%M')
# df_new = pd.DataFrame(index=nodes_names,columns=header)

# for h in range(total_simulations):
#     instant = datetime.time(hour=dss.solution.hour,minute=int(dss.solution.seconds // 60)).strftime('%H:%M')
#     dss.solution.solve()
    
#     bus_voltages = dss.circuit.buses_volts
#     df_new[instant] = [
#         (bus_voltages[j] + 1j * bus_voltages[j+1]) for j in range(0,len(bus_voltages),2)
#     ]

    


# # %%
# df_new['Bus'] = [
#     n.split('.')[0] for n in df_new.index
# ]
# df_new['Phase'] = [
#     n.split('.')[1] for n in df_new.index
# ]

# grouped_new = df_new.groupby('Bus')
# rows_subplot = len(df_new['Bus'].unique())//2 if len(df_new['Bus'].unique())%2 == 0 else len(df_new['Bus'].unique())//2 + 1

# # %%
# for bus,group in grouped_new:
#     group_transposed = group.T
#     group_transposed.columns = [f"Voltage_{p}" for p in group_transposed.loc['Phase']]
#     group_transposed = group_transposed.drop(index=['Bus','Phase'])
#     if 'Voltage_4' in group_transposed.columns:
#         group_transposed = group_transposed.drop(columns="Voltage_4")
#     group_transposed = group_transposed.map(abs)
#     group_transposed.index = group_transposed.index.map(str_to_time)
#     plt.figure()
    
#     for column in group_transposed.columns:
#         plt.plot(group_transposed.index, group_transposed[column], label=column)
    
#     plt.title(f'Tensão em função do horário para a barra {bus}')
#     plt.xlabel('Horário')
#     plt.ylabel('Tensão (V)')
#     plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#     plt.xticks(rotation=45)
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(f'voltage_plot_{bus}.png')  # Salvando o gráfico como imagem


# # %%

