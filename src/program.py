import datetime
import math
import os
import numpy as np
import pandas as pd
import py_dss_interface as pydss
import plotly.express as px


def str_to_time(string: str):
    return datetime.datetime.strptime(string, "%H:%M")


def initial_state_simulation(dss):
    # Desativando as baterias
    elements = dss.circuit.elements_names
    for element in elements:
        dss.circuit.set_active_element(element)
        if not (element.find("Generator.") == -1 and element.find("Storage.") == -1):
            if dss.cktelement.is_enabled == 1:
                dss.cktelement.enabled(0)
    dss.solution.solve()


def only_gd_simulation(dss):
    elements = dss.circuit.elements_names
    for element in elements:
        dss.circuit.set_active_element(element)
        if not (element.find("Storage.") == -1):
            if dss.cktelement.is_enabled == 1:
                dss.cktelement.enabled(0)
    dss.solution.solve()


def with_gd_storage_simulation(dss,storages):
    elements = dss.circuit.elements_names
    for element in elements:
        dss.circuit.set_active_element(element)
        if not (element.find("Storage.") == -1):
            if dss.cktelement.is_enabled == 1:
                dss.cktelement.enabled(0)
    for storage in storages:
        dss.text(f"New Storage.{storage['Barra']} phases=3 bus={storage['Barra']}.1.2.3.4 kV=0.22 kWRated={storage['Potencia nominal']} kWhrated={storage['Energia nominal']} dispmode=follow daily=CurvaBAT")
    dss.solution.solve()

def intialize_voltage_dataframes(v_monitors):

    va_df = pd.DataFrame(
        np.zeros((48, len(v_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    vb_df = pd.DataFrame(
        np.zeros((48, len(v_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    vc_df = pd.DataFrame(
        np.zeros((48, len(v_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    va_df.columns = v_monitors
    vb_df.columns = v_monitors
    vc_df.columns = v_monitors

    return {"va_df": va_df, "vb_df": vb_df, "vc_df": vc_df}


def initilalize_power_dataframes(p_monitors):
    pa_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    pb_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    pc_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    qa_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    qb_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    qc_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    p0_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    q0_df = pd.DataFrame(
        np.zeros((48, len(p_monitors))), index=np.arange(stop=24, start=0, step=0.5)
    )
    pa_df.columns = p_monitors
    pb_df.columns = p_monitors
    pc_df.columns = p_monitors
    qa_df.columns = p_monitors
    qb_df.columns = p_monitors
    qc_df.columns = p_monitors
    p0_df.columns = p_monitors
    q0_df.columns = p_monitors
    return {
        0: pa_df,
        1: qa_df,
        2: pb_df,
        3: qb_df,
        4: pc_df,
        5: qc_df,
        6: p0_df,
        7: q0_df,
    }


def get_power_dataframes(dss, monitors):

    p_monitors = [m for m in monitors if m.find("p_") != -1]
    print(p_monitors)
    p_dfs = initilalize_power_dataframes(p_monitors)
    dss.monitors.first()

    for _ in p_monitors:
        dss.monitors.name = _
        for key, value in p_dfs.items():
            value[_] = dss.monitors.channel(key + 1)

    return p_dfs


def get_voltage_dataframes(dss, monitors):
    v_monitors = [m for m in monitors if m.find("v_") != -1]
    print(v_monitors)
    v_dfs = intialize_voltage_dataframes(v_monitors)
    dss.monitors.first()
    for _ in v_monitors:
        dss.monitors.name = _
        v_dfs["va_df"][_] = dss.monitors.channel(1)
        v_dfs["vb_df"][_] = dss.monitors.channel(3)
        v_dfs["vc_df"][_] = dss.monitors.channel(5)
        v_dfs["va_df"][_] = v_dfs["va_df"][_].div(127)
        v_dfs["vb_df"][_] = v_dfs["vb_df"][_].div(127)
        v_dfs["vc_df"][_] = v_dfs["vc_df"][_].div(127)
    return v_dfs


## Instanciando o DSS
def programa(option="start-case",storage_specs=[]):
    
    
    dss = pydss.DSS()
    project_file = os.path.join(os.path.dirname(__file__), "circbtfull_storage.dss")
    dss.text(f"Compile {project_file}")
    dss.text("Set mode=daily")
    dss.text("Set stepsize=0.5h")
    dss.text("Set number=48")


    transformers = dss.transformers.names
    lines = dss.lines.names
    buses_monitored = []

    
    for l in lines:
        t1, t2 = l.split("_", 2)
        if not t1 in buses_monitored:
            dss.text(f"New Monitor.V_{t1} element =Line.{l} terminal=1 mode=0")
            buses_monitored.append(t1)
        if not t2 in buses_monitored:
            dss.text(f"New Monitor.V_{t2} element =Line.{l} terminal=2 mode=0")
            buses_monitored.append(t2)

    for t in transformers:
        dss.text(
            f"New Monitor.P_{t} element=Transformer.{t} terminal=1 mode=1 ppolar=no"
        )

    monitors = dss.monitors.names

    match option:
        case "start-case":
            initial_state_simulation(dss)
            powers = get_power_dataframes(dss, monitors)
            voltages = get_voltage_dataframes(dss, monitors)

        case "without-storage":
            only_gd_simulation(dss)
            powers = get_power_dataframes(dss, monitors)
            voltages = get_voltage_dataframes(dss, monitors)
        case "with-gd-storage":
            with_gd_storage_simulation(dss,storage_specs)
            powers = get_power_dataframes(dss, monitors)
            voltages = get_voltage_dataframes(dss, monitors)
        case _:
            return
        
        

    data = dict(
        {
            "va": voltages["va_df"].to_json(orient="split"),
            "vb": voltages["vb_df"].to_json(orient="split"),
            "vc": voltages["vc_df"].to_json(orient="split"),
            "pa": powers[0].to_json(orient="split"),
            "qa": powers[1].to_json(orient="split"),
            "pb": powers[2].to_json(orient="split"),
            "qb": powers[3].to_json(orient="split"),
            "pc": powers[4].to_json(orient="split"),
            "qc": powers[5].to_json(orient="split"),
            "p0": powers[6].to_json(orient="split"),
            "q0": powers[7].to_json(orient="split"),
        }
    )

    return data

    

    
    
    
    
    
if __name__ == "__main__":
    programa()
