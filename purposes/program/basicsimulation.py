################
#Práticas com OpenDSS e Python
#Manipulação de EnergyMeters e Medidores via Python
#Manipulação de Elementos do DSS via Python de forma iterativa (Exemplo com parâmetros de Geradores e Cargas)
#Trabalhando com Dataframes e Plots para a Análise de Resultados do DSS
#Versão: 1.2 
#Data da revisão: 09/12/2024
#Elaborado por: Prof. Pedro Henrique Aquino Barra (LADEE/UFU)
################


import os
import pandas as pd
import py_dss_interface
import numpy as np
import plotly_express as px
import math
import webbrowser

############################
### Simulação no OpenDSS ###
############################

dss = py_dss_interface.DSS()
dss.dssinterface.allow_forms = False ## Ativa as telas e plots do DSS 

### Chamando o dss file ###
file_dss = os.path.join(os.path.dirname(__file__), 'Master.dss') ## Chama o Master.dss usando a os

############################
### Executando o DSS #######
############################

dss.text(f"Compile [{file_dss}]")
dss.text("Set mode=daily")
dss.text("Set stepsize=1h")
dss.text("Set number=24")

#Explorando algumas coisas do circuito#
buses = dss.circuit.buses_names #comando para descobrir quais são as barras do meu circuito
lines = dss.lines.names #comando para descobrir quais são as barras do meu circuito
loads = dss.loads.names #comando para descobrir quais são as cargas do meu circuito

#Adicionando um EnergyMeter no início do alimentador (Line.l1)
dss.text("New Energymeter.E1 element=Line.l1 terminal=1") #adicionando um energymeter no alimentador 

##Adicionando alguns medidores de tensão nas linhas
for i in lines:
    dss.text(f"New Monitor.V_{i}_T1 element =Line.{i} terminal=1 mode=0") #mode=0 -> medição da tensões
    dss.text(f"New Monitor.V_{i}_T2 element =Line.{i} terminal=2 mode=0")

##Adicionando medidores de potência nos transformadores
transformers = dss.transformers.names
for _ in transformers:
    dss.text(f"New Monitor.P_{_} element =Transformer.{_} terminal=1 mode=1 ppolar=no") #mode=1 -> medição da potências || ppolar=no -> forma retangular (P+jQ)

#Dando Solve no circuito e plotando gráficos via DSS
dss.solution.solve()
dss.text("Plot monitor object= V_l1_T1 channels=(1 3 5)")
dss.text("Plot monitor object= V_feeder1_T1 channels=(1 3 5)")
dss.text("Plot monitor object= P_t1 channels=(1 3 5)")
dss.text("Plot monitor object= P_t2 channels=(1 3 5)")


########################################################
### Trabalhando com os resultados ("perdas elétricas")##
########################################################

feeder_energy = dss.meters.register_values[0] #O índice 0 (1 do elemento) retorna  o kWh do energy meter ativo
feeder_losses = dss.meters.register_values[12] #O índice 12 (13 do elemento) retorna as perdas do energy meter ativo
percentual_losses = (feeder_losses / feeder_energy) *100 
print("---")
print("Energia do alimentador: {:.4f} kWh".format(feeder_energy)) #4 casas decimais
print("Perdas do alimentador: {:.4f} kWh".format(feeder_losses))
print("Percentual de perdas: {:.4f}%".format(percentual_losses))
print("---")


##########################################################
### Trabalhando com os resultados ("tensões nas barras")##
##########################################################

#Quais monitores temos?
print("Medidores existentes:", dss.monitors.names)

#Escolha para análise: Tensão na carga - medidor 'v_carga'
dss.monitors._name_write('v_carga') #Ativação do medidor v_carga
#dss.monitors.header
v_load = pd.DataFrame(np.zeros((24, 3))) #Criação de um dataframe para v_carga
v_load.columns = ['Va (pu)', 'Vb(pu)', 'Vc(pu)'] #Nome para as colunas
v_load.iloc[:,0] = dss.monitors.channel(1) #V1
v_load.iloc[:,1] = dss.monitors.channel(3) #V2
v_load.iloc[:,2] = dss.monitors.channel(5) #V3
v_load = v_load.div((13800 / math.sqrt(3))) #[v] to [pu]

#Escolha para análise: Tensão na no alimentador feeder1 terminal 1 
dss.monitors._name_write('v_feeder1_t1') #Ativação do medidor
v_feeder_T1 = pd.DataFrame(np.zeros((24, 3))) #Criação de um dataframe para v_feeder1_t1
v_feeder_T1.columns = ['Va (pu)', 'Vb(pu)', 'Vc(pu)'] #Nome para as colunas
v_feeder_T1.iloc[:,0] = dss.monitors.channel(1) #V1
v_feeder_T1.iloc[:,1] = dss.monitors.channel(3) #V2
v_feeder_T1.iloc[:,2] = dss.monitors.channel(5) #V3
v_feeder_T1 = v_feeder_T1.div((13800 / math.sqrt(3))) #[v] to [pu]


#########################################################################
### Trabalhando com os resultados ("Carregamento dos transformadores")###
#########################################################################

dss.monitors._name_write('p_t1') #Ativação do medidor
#dss.monitors.header
p_SE = pd.DataFrame(np.zeros((24, 8))) #Criação de dataframe
p_SE.columns = [' P1 (kW)', ' Q1 (kvar)', ' P2 (kW)', ' Q2 (kvar)', ' P3 (kW)', ' Q3 (kvar)', ' P4 (kW)', ' Q4 (kvar)']
for i in range(len(p_SE.columns)): #Preechendo o dataframe de forma iterativa
    p_SE.iloc[:, i] = dss.monitors.channel(i + 1) #Indo do chanel 1 até o 8 (P1 até Q4)

dss.monitors._name_write('p_t2') #Ativação do medidor
p_GD = pd.DataFrame(np.zeros((24, 8)))
p_GD.columns = [' P1 (kW)', ' Q1 (kvar)', ' P2 (kW)', ' Q2 (kvar)', ' P3 (kW)', ' Q3 (kvar)', ' P4 (kW)', ' Q4 (kvar)']
for i in range(len(p_GD.columns)): #Preechendo o dataframe de forma iterativa
    p_GD.iloc[:, i] = dss.monitors.channel(i + 1)


###########
###Plots###
###########

###Tensão na Carga
config = {'toImageButtonOptions': {'format': 'svg'}}
v_load = v_load.reindex(sorted(v_load.columns), axis=1)
vload_plot = px.line(v_load, x=v_load.index, y=v_load.columns[0:])

vload_plot.update_layout(
    xaxis_title="Hora",
    yaxis_title="Tensão (pu)",
    legend_title="Legenda",
    plot_bgcolor="white",
    font=dict(size=25)
)
vload_plot.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
vload_plot.write_html(os.path.join(os.path.dirname(__file__), "figs/load_voltage.html"), config=config)
dir = os.path.join(os.path.dirname(__file__), "figs/load_voltage.html")
webbrowser.open(dir)

###Potência Trafo SE
config = {'toImageButtonOptions': {'format': 'svg'}}

p_SE = p_SE.reindex(sorted(p_SE.columns), axis=1)
p_SE_plot = px.line(p_SE, x=p_SE.index, y=p_SE.columns[0:])

p_SE_plot.update_layout(
    xaxis_title="Hora",
    yaxis_title="Potências",
    legend_title="Legenda",
    plot_bgcolor="white",
    font=dict(size=25)
)
p_SE_plot.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
p_SE_plot.write_html(os.path.join(os.path.dirname(__file__), "figs/sub_powers.html"), config=config)
dir = os.path.join(os.path.dirname(__file__), "figs/sub_powers.html")
webbrowser.open(dir)


################# 
##Prática 1: Desativando o Gerador
#################

dss.text(f"Compile [{file_dss}]")
dss.text("Set mode=daily")
dss.text("Set stepsize=1h")
dss.text("Set number=24")

#Adicionando um EnergyMeter no início do alimentador (Line.l1)
dss.text("New Energymeter.E1 element=Line.l1 terminal=1") #adicionando um energymeter no alimentador 

##Adicionando alguns medidores de tensão nas linhas
for i in lines:
    dss.text(f"New Monitor.V_{i}_T1 element =Line.{i} terminal=1 mode=0") #mode=0 -> medição da tensões
    dss.text(f"New Monitor.V_{i}_T2 element =Line.{i} terminal=2 mode=0")

##Adicionando medidores de potência nos transformadores
transformers = dss.transformers.names
for _ in transformers:
    dss.text(f"New Monitor.P_{_} element =Transformer.{_} terminal=1 mode=1 ppolar=no") #mode=0 -> medição da potências || ppolar=no -> forma retangular (P+jQ)

#### Desativando o gerador
dss.circuit.set_active_element('Generator.GD') #Antes de trabalhar com o GD preciso fazer com que este elemento fique ativo
dss.cktelement.enabled(0) #Com esse comando, estou desativando o elemento ativo (no caso, o gerador)
status_generator = dss.cktelement.is_enabled #Certificando que o generator está off (if status = 0 -> disabled)

if status_generator != 0:
    print("O gerador esta ativo: Verificar")

#Dando Solve no circuito e plotando gráficos via DSS 
dss.solution.solve()
dss.text("Plot monitor object= V_l1_T1 channels=(1 3 5)")
dss.text("Plot monitor object= V_feeder1_T1 channels=(1 3 5)")
dss.text("Plot monitor object= P_t1 channels=(1 3 5)")
dss.text("Plot monitor object= P_t2 channels=(1 3 5)") #Com o GD=OFF, esse transformador deve apresentar P->0


#################
##Prática 2: Alterando parâmetros dos circuitos (ex: parâmetros do gerador)
## Exemplo: Vamos variar o FP do gerador de 0.8 a 1.0 com passos de 0.05 e observar impactos em P+jQ e na tensão da carga
#################

PF = [0.8, 0.85, 0.90, 0.95, 1.00]
P_Generator = pd.DataFrame(np.zeros((24, 5))) #Criação de dataframe
P_Generator.columns = ['Pa FP080', 'Pa FP085', 'Pa FP090', 'Pa FP095', 'Pa FP1']
Q_Generator = pd.DataFrame(np.zeros((24, 5))) #Criação de dataframe
Q_Generator.columns = ['Qa FP080', 'Qa FP085', 'Qa FP090', 'Qa FP095', 'Qa FP1']
Va_load = pd.DataFrame(np.zeros((24, 5))) #Criação de dataframe
Va_load.columns = ['Va FP080', 'Va FP085', 'Va FP090', 'Va FP095', 'Va FP1']

aux = -1
for Z in PF:
    aux = aux +1
    dss.text(f"Compile [{file_dss}]")
    dss.text("Set mode=daily")
    dss.text("Set stepsize=1h")
    dss.text("Set number=24")

    #Adicionando um EnergyMeter no início do alimentador (Line.l1)
    dss.text("New Energymeter.E1 element=Line.l1 terminal=1") #adicionando um energymeter no alimentador 

    ##Adicionando alguns medidores de tensão nas linhas
    for i in lines:
        dss.text(f"New Monitor.V_{i}_T1 element =Line.{i} terminal=1 mode=0") #mode=0 -> medição da tensões
        dss.text(f"New Monitor.V_{i}_T2 element =Line.{i} terminal=2 mode=0")

    ##Adicionando medidores de potência nos transformadores
    transformers = dss.transformers.names
    for _ in transformers:
        dss.text(f"New Monitor.P_{_} element =Transformer.{_} terminal=1 mode=1 ppolar=no") #mode=0 -> medição da potências || ppolar=no -> forma retangular (P+jQ)

    #### Alterando parâmetros do gerador. 
    dss.circuit.set_active_element('Generator.GD') #Antes de trabalhar com o GD preciso fazer com que este elemento fique ativo
    dss.generators.kva = 1000
    dss.generators.pf = Z

    status_generator = dss.cktelement.is_enabled #Certificando que o generator está ON (if status = 1 -> ON)
    if status_generator != 1:
        print("O gerador esta desativado: Verificar")

    #Dando Solve no circuito e plotando gráficos via DSS
    dss.solution.solve()
    ##dss.text("Plot monitor object= V_l1_T1 channels=(1 3 5)")
    ##dss.text("Plot monitor object= V_feeder1_T1 channels=(1 3 5)")
    ##dss.text("Plot monitor object= P_t1 channels=(1 3 5)")
    ##dss.text("Plot monitor object= P_t2 channels=(1 3 5)") #Com o GD=OFF, esse transformador deve apresentar P->0
    #dss.text("Plot monitor object= P_t2 channels=(2 4 6)")
    P_Generator.iloc[:,aux] = dss.monitors.channel(1) #only phase A 
    Q_Generator.iloc[:,aux] = dss.monitors.channel(2) #only phase A

    #Escolha para análise: Tensão na carga - medidor 'v_carga'
    dss.monitors._name_write('v_carga') #Ativação do medidor v_carga
    #dss.monitors.header
    Va_load.iloc[:,aux] = dss.monitors.channel(1) #V1
    Va_load.iloc[:,aux] = Va_load.iloc[:,aux].div((13800 / math.sqrt(3))) #[v] to [pu]

#Plot rápido para observar os impactos
###Potência Ativa Gerador
P_Generator = P_Generator.reindex(sorted(P_Generator.columns), axis=1)
p_G_plot = px.line(P_Generator, x=P_Generator.index, y=P_Generator.columns[0:])

p_G_plot.update_layout(
    xaxis_title="Hora",
    yaxis_title="Potência Ativa (kW)",
    legend_title="Legenda",
    plot_bgcolor="white",
    font=dict(size=25)
)
p_G_plot.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
p_G_plot.write_html(os.path.join(os.path.dirname(__file__), "figs/p_G_plot.html"), config=config)
dir = os.path.join(os.path.dirname(__file__), "figs/p_G_plot.html")
webbrowser.open(dir)

###Potência Reativa Gerador
Q_Generator = Q_Generator.reindex(sorted(Q_Generator.columns), axis=1)
Q_G_plot = px.line(Q_Generator, x=Q_Generator.index, y=Q_Generator.columns[0:])

Q_G_plot.update_layout(
    xaxis_title="Hora",
    yaxis_title="Potência Reativa (kvar)",
    legend_title="Legenda",
    plot_bgcolor="white",
    font=dict(size=25)
)
Q_G_plot.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
Q_G_plot.write_html(os.path.join(os.path.dirname(__file__), "figs/q_G_plot.html"), config=config)
dir = os.path.join(os.path.dirname(__file__), "figs/q_G_plot.html")
webbrowser.open(dir)

###Tensão na carga com FP do Gerador variando
Va_load = Va_load.reindex(sorted(Va_load.columns), axis=1)
Va_load_plot = px.line(Va_load, x=Va_load.index, y=Va_load.columns[0:])

Va_load_plot.update_layout(
    xaxis_title="Hora",
    yaxis_title="Tensão (pu)",
    legend_title="Legenda",
    plot_bgcolor="white",
    font=dict(size=25)
)
Va_load_plot.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
Va_load_plot.write_html(os.path.join(os.path.dirname(__file__), "figs/Va_load_plot.html"), config=config)
dir = os.path.join(os.path.dirname(__file__), "figs/Va_load_plot.html")
webbrowser.open(dir)


#################
##Prática 3: Processo Iterativo para Alocação de Cargas
## Exemplo: Imagine que a energia medida neste alimentador seja de 85000 kWh para o período simulado. Faça um procedimento de "alocação de cargas" para obter Emedida = Esimulada
## Módulo interessante, pois é similar ao feito no processo da ANEEL do cálculo de perdas técnicas, na etapa de alocação de cargas
#################

def update_loads(energy_factor): # Função que atualizar o kW e o kvar de todas as cargas (nesse cirtuito, uma apenas)
    dss.loads.first() # Comando que lista todas as loads do circuito analisado e ativa a primeira 
    for _ in range(dss.loads.count): # Laço para varrer todas as cargas do circuito
        dss.loads.kw = dss.loads.kw * energy_factor # Pega o kW atual e multiplica por um fator que é input da função
        dss.loads.kvar = dss.loads.kvar * energy_factor # Pega o kvar atual e multiplica por um fator que é input da função      
        dss.loads.next() # Atualizado o kW e o kvar da carga n, passo para a carga n+1. Isso se repete até a última carga do circuito

df_index = list(range(0, 1))
loadallocation_sumary = pd.DataFrame(index=df_index, columns=['Measured Energy (kWh)', 'Power Flow Energy (kWh)', 'Error (%)', 'Power Flow Losses (kWh)', 'Power Flow Losses (%)', 'Energy Factor', 'Iterations'])
energy_factor = 1 #No início, energy_factor = 1 faz com que os kW-kvar sejam os inicialmente declarados
num_iterations = 0
convergence = False
measured_energy = 85000 #Input da energia medida (ex: obtida via BDGD)
while not convergence:
    dss.text(f"Compile [{file_dss}]")
    update_loads(energy_factor)
    dss.text("Set mode=daily")
    dss.text("Set stepsize=1h")
    dss.text("Set number=24")
    dss.text("New Energymeter.E1 element=Line.l1 terminal=1") #adicionando um energymeter no alimentador 
    dss.solution.solve()

    feeder_energy = dss.meters.register_values[0] #índice 0 (1 do elemento) pega o kWh do energy meter
    feeder_losses = dss.meters.register_values[12] #índice 12 (13 do elemento) pega perdas
    percentual_losses = (feeder_losses / feeder_energy) *100

    delta_energy_kwh = measured_energy - feeder_energy #Obtém diferença entre o medido e o simulado
    print("Erro atual:", abs((measured_energy - feeder_energy) / measured_energy * 100), "%")
    print("Iteracao:", num_iterations)
 
    if abs((measured_energy - feeder_energy) / measured_energy * 100) < 0.01: #Critério de convergência: 0,01%. Quando tiver abaixo desse valor, assume-se convergência e imprime resultados.
        print(f'Energia Medida (kWh): {round(measured_energy, 2)}')
        print(f'Energia Simulada (kWh): {round(feeder_energy, 2)}')
        print(f'Perdas Elétricas (kWh): {round(feeder_losses, 2)}')
        print(f'Percentual das Perdas (%): {round(feeder_losses / feeder_energy * 100, 2)}')
        print(f'Energy Factor: {energy_factor}')
        print(f'Iterações: {num_iterations}')

        loadallocation_sumary.loc[num_iterations, 'Measured Energy (kWh)'] = round(measured_energy, 2)
        loadallocation_sumary.loc[num_iterations, 'Power Flow Energy (kWh)'] = round(feeder_energy, 2)
        loadallocation_sumary.loc[num_iterations, 'Error (%)'] = round( abs((measured_energy - feeder_energy) / measured_energy * 100), 5)
        loadallocation_sumary.loc[num_iterations, 'Power Flow Losses (kWh)'] = round(feeder_losses, 2)
        loadallocation_sumary.loc[num_iterations, 'Power Flow Losses (%)'] = round(feeder_losses / feeder_energy * 100, 2)
        loadallocation_sumary.loc[num_iterations, 'Energy Factor'] = energy_factor
        loadallocation_sumary.loc[num_iterations, 'Iterations'] = num_iterations
        convergence = True

        

    loadallocation_sumary.loc[num_iterations, 'Measured Energy (kWh)'] = round(measured_energy, 2)
    loadallocation_sumary.loc[num_iterations, 'Power Flow Energy (kWh)'] = round(feeder_energy, 2)
    loadallocation_sumary.loc[num_iterations, 'Error (%)'] = round( abs((measured_energy - feeder_energy) / measured_energy * 100), 5)
    loadallocation_sumary.loc[num_iterations, 'Power Flow Losses (kWh)'] = round(feeder_losses, 2)
    loadallocation_sumary.loc[num_iterations, 'Power Flow Losses (%)'] = round(feeder_losses / feeder_energy * 100, 2)
    loadallocation_sumary.loc[num_iterations, 'Energy Factor'] = energy_factor
    loadallocation_sumary.loc[num_iterations, 'Iterations'] = num_iterations

    energy_factor = energy_factor * (delta_energy_kwh / measured_energy + 1) #Não convergiu (erro<0,01%): calcula fator, incrementa número de iterações e executa fluxo de potência novamente.
    num_iterations += 1


###Erro versus iteração
Erros = loadallocation_sumary['Error (%)'].tolist()
Erros_plot = px.line(y=Erros)

Erros_plot.update_layout(
    xaxis_title="Iteração",
    yaxis_title="Erro (%)",
    legend_title="Legenda",
    plot_bgcolor="white",
    font=dict(size=25)
)
Erros_plot.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey'
)
Erros_plot.write_html(os.path.join(os.path.dirname(__file__), "figs/Erros_plot.html"), config=config)
dir = os.path.join(os.path.dirname(__file__), "figs/Erros_plot.html")
webbrowser.open(dir)

print("")


''''##fig problems:
pip install plotly --upgrade
Use o terminal interativo (Ctrl+Shift+P > "Python: Run Python File in Terminal")
'''
