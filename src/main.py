import datetime

import numpy as np
import pandas as pd
import py_dss_interface as pydss
import seaborn as sns
import matplotlib.pyplot as plt


def float_to_time(hours_float):
    start_date = datetime.datetime(2024, 11, 20)
    time_delta = datetime.timedelta(hours=hours_float)
    time_obj = (start_date + time_delta).time()

    return str(time_obj)


def get_monitor_data(name: str):
    dssObj.monitors.name = name
    dssObj.monitors.save()
    num_channels = dssObj.monitors.num_channels
    header = dssObj.monitors.header
    data = {}
    for i in range(num_channels):
        data[header[i]] = dssObj.monitors.channel(i + 1)
    return {"monitor_name": name, "data": data}


# dssObj = pydss.DSS()
# dss_project_file = r"C:/Users/gabri/project-tcc/src/circbtfull_storage.dss"
# dssObj.text(f"compile {dss_project_file}")
# dssObj.solution.mode = 1
# dssObj.solution.step_size = 600
# dssObj.solution.number = 24 * 6
# dssObj.solution.solve()

# name_monitors = dssObj.monitors.names
# monitors_obj = []
# for name in name_monitors:
#     monitors_obj.append(get_monitor_data(name))
# dfs = dict(
#     map(lambda d: (d["monitor_name"], pd.DataFrame(data=d["data"])), monitors_obj)
# )
# df = dfs[name_monitors[0]]

# sns.lineplot(data=df[df.columns[0:6:2]])
# plt.show()


## Instancia Cicuito inicial


dssObj = pydss.DSS()
project_file = r"C:/Users/gabri/project-tcc/src/circbtfull_storage.dss"


dssObj.text(f"compile {project_file}")

nodes_names = dssObj.circuit.nodes_names
elements_names = dssObj.circuit.elements_names
num_buses = dssObj.circuit.num_buses
num_cktelement = dssObj.circuit.num_ckt_elements


## Desabilitando todos os geradores fotovoltaicos

for element in elements_names:
    dssObj.circuit.set_active_element(element)
    if not (element.find("Generator.") == -1  and element.find("Storage.") == -1) :
        if dssObj.cktelement.is_enabled == 1:
            dssObj.cktelement.enabled(0)
            print(f"{element} is disabled")


# Setando configurações básicas das simulações
dssObj.solution.mode = 1
dssObj.solution.stepsize = 60
dssObj.solution.number = 24 * 60

dssObj.solution.solve()


circuit_buses = np.array(dssObj.circuit.buses_names)


print(circuit_buses)
print(elements_names)


## Análise sem baterias e geradores - Compreendendo o status inicial da rede





print(' FIM ')



