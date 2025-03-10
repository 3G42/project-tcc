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
    p_dfs = initilalize_power_dataframes(p_monitors)
    dss.monitors.first()

    for _ in p_monitors:
        dss.monitors.name = _
        for key, value in p_dfs.items():
            value[_] = dss.monitors.channel(key + 1)

    return p_dfs


def get_voltage_dataframes(dss, monitors):
    v_monitors = [m for m in monitors if m.find("v_") != -1]
    v_dfs = intialize_voltage_dataframes(v_monitors)
    dss.monitors.first()
    for _ in v_monitors:
        dss.monitors.name = _
        v_dfs["va_df"][_] = dss.monitors.channel(1)
        v_dfs["vb_df"][_] = dss.monitors.channel(3)
        v_dfs["vc_df"][_] = dss.monitors.channel(5)

    return v_dfs

def volts_to_pu(voltage: pd.DataFrame):
    for column in voltage.columns:
        voltage[column] = voltage[column].div(127)
    
    return voltage

## Instanciando o DSS
def programa(option="without-storage",storage_specs=[]):
    
    
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
    

    
    v_buses_quality = pd.DataFrame()
    for column in voltages['va_df'].columns:
        v_buses_quality[column] = voltage_quality(voltages,column)
    data = dict(
        {
            "va": volts_to_pu(voltages["va_df"]).to_json(orient="split"),
            "vb": volts_to_pu(voltages["vb_df"]).to_json(orient="split"),
            "vc": volts_to_pu(voltages["vc_df"]).to_json(orient="split"),
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


def voltage_quality(voltages,column):
    ## Calculando DRP e DRC

    # Calculando DRP e DRC fase A
    registros_precaria_inferior_a = sum(1 for valor in voltages["va_df"][column] if valor >= 110 and valor < 117)
    registros_precaria_superior_a = sum(1 for valor in voltages["va_df"][column] if valor > 133 and valor <= 135)
    DRP_A = 100*((registros_precaria_superior_a + registros_precaria_inferior_a)) / len(voltages["va_df"][column])
    registros_critica_inferior_a = sum(1 for valor in voltages["va_df"][column] if valor < 110)
    registros_critica_superior_a = sum(1 for valor in voltages["va_df"][column] if valor > 135)
    DRC_A = 100*((registros_critica_superior_a + registros_critica_inferior_a)) / len(voltages["va_df"][column])

    # Calculando DRP e DRC fase B
    registros_precaria_inferior_b = sum(1 for valor in voltages["vb_df"][column] if valor >= 110 and valor < 117)
    registros_precaria_superior_b = sum(1 for valor in voltages["vb_df"][column] if valor > 133 and valor <= 135)
    DRP_B = 100*((registros_precaria_superior_b + registros_precaria_inferior_b)) / len(voltages["vb_df"][column])
    registros_critica_inferior_b = sum(1 for valor in voltages["vb_df"][column] if valor < 110)
    registros_critica_superior_b = sum(1 for valor in voltages["vb_df"][column] if valor > 135)
    DRC_B = 100*((registros_critica_superior_b + registros_critica_inferior_b)) / len(voltages["vb_df"][column])

    # Calculando DRP e DRC fase C
    registros_precaria_inferior_c = sum(1 for valor in voltages["vc_df"][column] if valor >= 110 and valor < 117)
    registros_precaria_superior_c = sum(1 for valor in voltages["vc_df"][column] if valor > 133 and valor <= 135)
    DRP_C = 100*((registros_precaria_superior_c + registros_precaria_inferior_c)) / len(voltages["vc_df"][column])
    registros_critica_inferior_c = sum(1 for valor in voltages["vc_df"][column] if valor < 110)
    registros_critica_superior_c = sum(1 for valor in voltages["vc_df"][column] if valor > 135)
    DRC_C = 100*((registros_critica_superior_c + registros_critica_inferior_c)) / len(voltages["vc_df"][column])

    # Calculando o percentil 99% e 1%
    percentil_99_a = np.percentile(voltages["va_df"][column], 99)
    percentil_1_a = np.percentile(voltages["va_df"][column], 1)
    percentil_99_b = np.percentile(voltages["vb_df"][column], 99)
    percentil_1_b = np.percentile(voltages["vb_df"][column], 1)
    percentil_99_c = np.percentile(voltages["vc_df"][column], 9)
    percentil_1_c = np.percentile(voltages["vc_df"][column], 1)
    
    print(f'************ BARRA {column} *****************************************')
    print('************ Indicadores de tensão em regime permanente **************')
    print('                Fase A        Fase B       Fase C')
    print(f'DRP (%)         {DRP_A:0.2f}          {DRP_B:0.2f}         {DRP_C:0.2f}')
    print(f'DRC (%)         {DRC_A:0.2f}          {DRC_B:0.2f}         {DRC_C:0.2f}')
    print(f'P99% (V)        {percentil_99_a:0.2f}        {percentil_99_b:0.2f}       {percentil_99_c:0.2f}')
    print(f'P1% (V)         {percentil_1_a:0.2f}        {percentil_1_b:0.2f}       {percentil_1_c:0.2f}')
    print('**********************************************************************')
    
    
    
if __name__ == "__main__":
    programa()
