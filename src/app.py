from io import StringIO
import json
from typing import Any, Dict, List, Union
from dash import (
    Dash,
    html,
    dcc,
    Input,
    Output,
    callback,
    State,
    dash_table,
    callback_context,
)
import pandas as pd
from dash.exceptions import PreventUpdate

from program import programa
import plotly.express as px


import dash_mantine_components as dmc

params_storage = ["Barra", "Potencia nominal", "Energia nominal"]

simulation_types = [["without-gd-storage", "Sem GD e sem armazenamento"],
                    ["with-gd-without-storage", "Com GD e sem armazenamento"], ["with-gd-storage", "Com GD e com armazenamento"]]


value_types = [
    {"label": "Tensão (va)", "value": "va"},
    {"label": "Tensão (vb)", "value": "vb"},
    {"label": "Tensão (vc)", "value": "vc"},
    {"label": "Potência ativa (pa)", "value": "pa"},
    {"label": "Potência ativa (pb)", "value": "pb"},
    {"label": "Potência ativa (pc)", "value": "pc"},
    {"label": "Potência reativa (qa)", "value": "qa"},
    {"label": "Potência reativa (qb)", "value": "qb"},
    {"label": "Potência reativa (qc)", "value": "qc"},
]


app = Dash(__name__,external_stylesheets=dmc.styles.ALL)
app.layout = dmc.MantineProvider(
    [
        # HEADER
        dmc.Flex(
                    [
                        dmc.Title(
                            children="Simulador de Redes Elétricas",
                            order=1,
                            c="blue.9",
                            
                        ),
                        dmc.Text(
                            "Análise do efeito da geração distribuída e armazenamento em uma rede elétrica de BT",
                            c="gray.8",
                            ta="center",
                            size="lg"
                        ),
                    ],
                    className="header",
                    direction="column",
                    align="center",
                    justify="space-evenly",
                    gap="md",
                    pt="lg",
                    pb="md",
                ),
        
        
        # Seletor de simulação
        dmc.Flex(
                    children=[
                        dmc.Title(
                            "Simulação",
                            className='menu-title',
                            order=6,
                            w="100%"
                        ),
                        dmc.Select(
                            id="simulation-select",
                            data=[],
                            placeholder="Selecione a simulação",
                            disabled=True,   
                            maw="800px",
                            w="80%"                          
                        ),
                        dmc.Button(
                            "Nova simulação",
                            id="new-simulation-button",
                            w="fit-content",
                        )
                    ],
                    direction="row",
                    wrap="wrap",
                    justify="space-between",
                    my="md",
                    mx="md",
                    style={"boxSize": "content-box"},
                    
                    
                ),
        dmc.Modal(
            title="Nova simulação",
            id="modal-simple",
            size='lg',
            children=[
                dmc.RadioGroup(
                    id="simulation-type",
                    children=dmc.Group([dmc.Radio(l,value=k) for k,l in simulation_types], my=10),
                    value="without-gd-storage",
                    label="Selecione o tipo de simulação",
                    size="sm",
                    mb=10,
                    required=True
                ),
                dmc.Flex(
                    children=[
                        dmc.Select(
                            id="bus-select",
                            data=[{'value':f"bus-{i}", "label": f"Barra {i}"} for i in range(1,18)],
                            label="Barra",
                            mb=10,
                            w="30%"
                        ),
                        dmc.TextInput(label="Potência nominal", mb=10, id="power-input",
                            w="30%"),
                        dmc.TextInput(label="Energia nominal", mb=10, id="energy-input",
                            w="30%"),
                        dmc.Button("Adicionar", w="fit-content", mb=10, id="add-storage-button"),
                        dmc.Table(
                            id="storage-table",
                            data={
                                'head':["Barra", "Potência nominal", "Energia nominal"],
                                'body':[],
                            }
                        )
                    ],
                    id="storages-form-container",
                    direction="row",
                    wrap="wrap",
                    gap="sm",
                    align="center",
                    justify="space-between",
                    display="none"
                ),
                dmc.Space(h=20),
                dmc.Group(children=[
                    dmc.Button("Salvar", id="save-button", w="fit-content"),
                    dmc.Button("Cancelar", w="fit-content", id="cancel-button", color="red", variant="outline"),
                    
                ],justify="flex-end",gap="sm",w="100%"),
                
            ],
            style={"display": "flex", "flexDirection": "column", 'justifyContent': "center", 'alignItems': "center"},
            ),
        dmc.Select(
            id="value-select",
            label="Selecione as variáveis a serem monitoradas",
            value=[],
            data=value_types,
            disabled=True,
            maw="800px",
            w="80%",
            my="md",
            mx="md",
        ),
        dcc.Graph(id="graph", style={"display": "none"}),
        dcc.Store(id="simulations"),
    ],
    
)






@callback(
    Output('modal-simple','opened'),
    Input('new-simulation-button','n_clicks'),
    Input('cancel-button','n_clicks'),
    Input('simulations','data'),
    State('modal-simple','opened'),
    prevent_initial_call=True
)
def toggle_modal(new_click, close_click, simulations ,opened):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "new-simulation-button":
        return True
    elif input_id == "cancel-button":
        return False
    elif input_id == "simulations":
        return not opened
    return opened
    
    

@callback(
    Output('storages-form-container','display'),
    Input('simulation-type','value'),
    prevent_initial_call=True
) 
def show_storage_form(value):
    if value == "with-gd-storage":
        return "flex"
    return "none"

@callback(
    Output('storage-table','data'),
    Input('add-storage-button','n_clicks'),
    Input('save-button','n_clicks'),
    Input('cancel-button','n_clicks'),
    State('bus-select','value'),
    State('power-input','value'),
    State('energy-input','value'),
    State('storage-table','data'),
    prevent_initial_call=True,
)
def control_storage(n_clicks,save,cancel,bus: str,power,energy,data:dict[str,list[str|list[str]]]):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "add-storage-button":
        if n_clicks > 0:
            head = data['head']
            body = data['body']
            body.append([int(bus.split('-')[-1]),float(power),float(energy)])
            return {'head':head,'body':body}
    elif input_id == "save-button":
        if save > 0:
            return {'head':data['head'],'body':[]}
    elif input_id == "cancel-button":
        if cancel > 0:
            return {'head':data['head'],'body':[]}
    else:
        return data

@callback(
    Output('simulations','data'),
    Input('save-button','n_clicks'),
    State('simulation-type','value'),
    State('storage-table','data'),
    State('simulations','data'),
    prevent_initial_call=True,
)
def add_simulation(n_clicks,type:str,storage_data:Dict[str,List[Union[str, List[Union[str,float]]]]],previous_data):
    if n_clicks > 0:
        storage = [f"Bus:{a[0]} Power:{a[1]} Energy:{a[2]}" for a in storage_data['body']]
        id_value = f"{type.replace('-',' ').capitalize()} {' and '.join(storage)}"
        hash_value = hash(id_value)
        previous = {} if previous_data is  None else json.loads(previous_data)
        if hash_value in previous.keys():
            return previous_data
        simulation = programa(id_value,type,storage_data['body'])
        previous[hash_value] = simulation
        data = json.dumps(previous)
        
        return data
    return previous_data

@callback(
    Output('simulation-select','data'),
    Output('simulation-select','disabled'),
    Output('value-select','disabled'),
    Input('simulations','data'),
    prevent_initial_call=True
)
def update_simulation_select(data):
    if data is None:
        return [],True,True
    obj:dict = json.loads(data)
    options = []
    for k,v in obj.items():
        options = options + [{'label':v['id'],'value':k}]
    return options,False,False

@callback(
    Output('graph','style'),
    Output('graph','figure'),
    Input('value-select','value'),
    State('simulation-select','value'),
    State('simulations','data'),
)
def select_graph(value,simulation,data):
    if simulation is None or data is None:
        raise PreventUpdate
    obj = json.loads(data)

    simulation_data = obj[simulation]
    if simulation_data is None or value is None:
        raise PreventUpdate
    
    df = pd.DataFrame(**(json.loads(simulation_data[value])))
    if df.empty:
        raise PreventUpdate
    
    fig = px.line(df,x=df.index,y=df.columns)
    fig.update_layout(
        xaxis_title='Hora',
        yaxis_title=f"{'Tensão' if value == "va" or value=='vb'or value =='vc' else 'Potência'} (pu)",
        legend_title=f"{'Tensão' if value == "va" or value=='vb' or value =='vc' else 'Potência'}",
        plot_bgcolor="white",
        font=dict(size=25)
        )
    return {"display": "block"},fig

@callback(
    Output('value-select','value'),
    Input('simulation-select','value'),
    
)
def clear_select(value):
    if value is None:
        raise PreventUpdate
    return None


if __name__ == "__main__":
    app.run(debug=True)
