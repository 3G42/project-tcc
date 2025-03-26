from io import StringIO
import json
from typing import Any, Dict, List
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

from header.Header import Header

import dash_mantine_components as dmc

params_storage = ["Barra", "Potencia nominal", "Energia nominal"]

simulation_types = [["without-gd-storage", "Sem GD e sem armazenamento"],
                    ["with-gd-without-storage", "Com GD e sem armazenamento"], ["with-gd-storage", "Com GD e com armazenamento"]]





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
                dmc.TextInput(label="Nome da simulação", placeholder="Insira o nome da simulação", mb=10,required=True,id="simulation-name"),
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
                    dmc.Button("Cancelar", w="fit-content", id="modal-close-button", color="red", variant="outline"),
                    
                ],justify="flex-end",gap="sm",w="100%"),
                
            ],
            style={"display": "flex", "flexDirection": "column", 'justifyContent': "center", 'alignItems': "center"},
            ),
        dcc.Graph(id="graph", style={"display": "none"}),
        dcc.Store(id="simulations"),
    ],
    
)






@callback(
    Output('modal-simple','opened'),
    Input('new-simulation-button','n_clicks'),
    Input('modal-close-button','n_clicks'),
    Input('simulations','data'),
    State('modal-simple','opened'),
    prevent_initial_call=True
)
def toggle_modal(new_click, close_click, simulations ,opened):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "new-simulation-button":
        return True
    elif input_id == "modal-close-button":
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
    State('bus-select','value'),
    State('power-input','value'),
    State('energy-input','value'),
    State('storage-table','data'),
    prevent_initial_call=True,
)
def add_storage(n_clicks,bus: str,power,energy,data:dict[str,list[str|list[str]]]):
    if n_clicks > 0:
        head = data['head']
        body = data['body']
        body.append([int(bus.split('-')[-1]),float(power),float(energy)])
        return {'head':head,'body':body}
    return data

@callback(
    Output('simulations','data'),
    Input('save-button','n_clicks'),
    State('simulation-name','value'),
    State('simulation-type','value'),
    State('storage-table','data'),
    State('simulations','data'),
    prevent_initial_call=True,
)
def add_simulation(n_clicks,name,type,storage_data,previous_data):
    if n_clicks > 0:
        id_value = f"{name}-{type}-{str(storage_data['body'])}"
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
    Input('simulations','data'),
    prevent_initial_call=True
)
def update_simulation_select(data):
    if data is None:
        return [],True
    obj = json.loads(data)
    keys= [x for x in obj.keys()]
    ids : list[str] = [x['id'] for x in obj.values()]
    ids = [id.replace('-',' ').replace('[','').replace(']','').capitalize() for id in ids]
    return ids,False

@callback(
    Output('graph','style'),
    Output('graph','figure'),
    Input('simulation-select','value'),
    State('simulations','data'),
)
def select_graph(simulation,data):
    if simulation is None or data is None:
        raise PreventUpdate
    obj = json.loads(data)
    simulation_id = [k for k,v in obj.items() if v['id'] == simulation][0]
    simulation_data = obj[simulation_id]
    if simulation_data['type'] == 'without-gd-storage':
        df = pd.DataFrame(**simulation_data['data'])
        fig = px.line(df,x=df.index,y=df.columns)
        fig.update_layout(
            xaxis_title='Hora',
            yaxis_title="Tensão (pu)",
            legend_title="Legenda",
            plot_bgcolor="white",
            font=dict(size=25)
            )
        return {"display": "block"},fig
    elif simulation_data['type'] == 'with-gd-without-storage':
        df = pd.DataFrame(**simulation_data['data'])
        fig = px.line(df,x=df.index,y=df.columns)
        fig.update_layout(
            xaxis_title='Hora',
            yaxis_title="Potência (pu)",
            legend_title="Legenda",
            plot_bgcolor="white",
            font=dict(size=25)
            )
        return {"display": "block"},fig
    elif simulation_data['type'] == 'with-gd-storage':
        df = pd.DataFrame(**simulation_data['data'])
        fig = px.line(df,x=df.index,y=df.columns)
        fig.update_layout(
            xaxis_title='Hora',
            yaxis_title="Potência (pu)",
            legend_title="Legenda",
            plot_bgcolor="white",
            font=dict(size=25)
            )
        return {"display": "block"},fig
    return {"display": "none"},None


# @callback(
#     Input("new-simulation-button", "n_clicks"),
#     prevent_initial_call=True,
#     )
# @callback(
#     Output("simulations", "data"),
#     Output("graph-dropdown", "options"),
#     Output("graph-dropdown", "value"),
#     Output("storages-form-container", "className"),
#     Input("simulation-select", "value"),
#     Input("save-button", "n_clicks"),
#     State("table-editing-simple", "data"),
#     State("simulations", "data"),
#     prevent_initial_call=True,
# )
# def select_simulation(sim, n_clicks, storages_data, previous_data):
#     if sim is None:
#         return None, None, None
#     else:
#         if previous_data is None:
#             previous = {}
#         else:
#             previous = json.loads(previous_data)
#             if sim in previous:
#                 return (
#                     previous_data,
#                     {"V": "Tensão", "P": "Potência", "E": "Energia"},
#                     None,
#                     (
#                         "form-container"
#                         if sim == "with-gd-storage"
#                         else "form-container disabled"
#                     ),
#                 )
#         if sim == "with-gd-storage":
#             json_data = programa(sim, storages_data)
#         else:
#             json_data = programa(sim)
#         previous[sim] = json_data
#         data = json.dumps(previous)
#         return (
#             data,
#             {"V": "Tensão", "P": "Potência", "E": "Energia"},
#             None,
#             "form-container" if sim == "with-gd-storage" else "form-container disabled",
#         )


# @callback(
#     Output("graph-select", "style"),
#     Output("graph-select", "options"),
#     Input("graph-dropdown", "value"),
#     prevent_initial_call=True,
# )
# def select_graph(val):
#     if val is None:
#         raise PreventUpdate
#     match val:
#         case "V":
#             return {"display": "block"}, [
#                 {"label": "Fase A", "value": "va"},
#                 {"label": "Fase B", "value": "vb"},
#                 {"label": "Fase C", "value": "vc"},
#             ]
#         case "P":
#             return {"display": "block"}, [
#                 {"label": "Fase A", "value": "pa"},
#                 {"label": "Fase B", "value": "pb"},
#                 {"label": "Fase C", "value": "pc"},
#                 {"label": "Neutro", "value": "p0"},
#             ]


# @callback(
#     Output("graph", "figure"),
#     Input("graph-select", "value"),
#     Input("bus-select", "value"),
#     State("simulations", "data"),
#     State("simulation-select", "value"),
#     prevent_initial_call=True,
# )
# def select_graph_type(val, bus, data, sim):
#     ctx = callback_context
#     input_id = ctx.triggered[0]["prop_id"].split(".")[0]
#     if val is None or data is None:
#         raise PreventUpdate
#     store = json.loads(data)
#     dictionary = store[sim]
#     if input_id == "graph-select":

#         match val:
#             case "va" | "vb" | "vc":
#                 dff = pd.DataFrame(**(json.loads(dictionary[val])))
#                 v_plot = px.line(dff, x=dff.index, y=dff.columns[0:])
#                 v_plot.update_layout(
#                     xaxis_title="Hora",
#                     yaxis_title="Tensão (pu)",
#                     legend_title="Legenda",
#                     plot_bgcolor="white",
#                     font=dict(size=25),
#                 )
#                 return v_plot
#             case "pa" | "pb" | "pc" | "p0":
#                 dff = pd.DataFrame(**(json.loads(dictionary[val])))
#                 p_plot = px.line(dff, x=dff.index, y=dff.columns[0:])
#                 p_plot.update_layout(
#                     xaxis_title="Hora",
#                     yaxis_title="Potência (pu)",
#                     legend_title="Legenda",
#                     plot_bgcolor="white",
#                     font=dict(size=25),
#                 )
#                 return p_plot
#             case _:
#                 return None
#     elif input_id == "bus-select":
#         if val == [] or bus == []:
#             raise PreventUpdate
#         if val == None:
#             raise PreventUpdate
#         if val == "va" or val == "vb" or val == "vc":
#             dff = pd.DataFrame(**(json.loads(dictionary[val])))
#             v_plot = px.line(dff, x=dff.index, y=[dff[f"v_p{b}"] for b in bus])
#             v_plot.update_layout(
#                 xaxis_title="Hora",
#                 yaxis_title="Tensão (pu)",
#                 legend_title="Legenda",
#                 plot_bgcolor="white",
#                 font=dict(size=25),
#             )
#             return v_plot


# @callback(
#     Output("table-editing-simple", "data"),
#     Input("editing-rows-button", "n_clicks"),
#     State("bar-number", "value"),
#     State("power-input", "value"),
#     State("energy-input", "value"),
#     State("table-editing-simple", "data"),
#     State("table-editing-simple", "columns"),
# )
# def add_row(n_clicks, bar, power, energy, data, columns):
#     if n_clicks > 0:
#         data.append(
#             {"Barra": bar, "Potencia nominal": power, "Energia nominal": energy}
#         )
#     return data


# @callback(
#     Output("table-container", "style"),
#     Input("editing-rows-button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def show_table(n_clicks):
#     if n_clicks > 0:
#         return {"display": "block"}
#     else:
#         return {"display": "none"}


# @callback(
#     Output("table-editing-simple", "editable"),
#     Output("editing-rows-button", "disabled"),
#     Output("storages-form-container", "style", allow_duplicate=True),
#     Output("save-button", "style"),
#     Input("save-button", "n_clicks"),
#     State("table-editing-simple", "data"),
#     prevent_initial_call=True,
# )
# def update_storage(n_clicks, data):
#     if data == []:
#         return True, False, {"display": "block"}, {"display": "block"}
#     if n_clicks > 0:

#         return False, True, {"display": "none"}, {"display": "none"}
#     return True, False, {"display": "block"}, {"display": "block"}


# # @callback(
# #     Output('graph-dropdown', 'disabled'),
# #     State('simulation-select','value'),

# # )

# # @callback(
# #     Output('intermediate-value','data'),
# #     Input('dropdown-1','value'),

# # )
# # def select_graph_type(val):
# #     if val is None:
# #         # PreventUpdate prevents ALL outputs updating
# #         raise PreventUpdate
# #     ## Quero converter a pd.Series de Dataframes, para um json
# #     json_data = programa()

# #     json_data = json.dumps(json_data)
# #     print(json_data)
# #     return json_data


# # @callback(
# #     Output('graph', 'figure'),
# #     Input('intermediate-value', 'data'),
# #     Input('dropdown-2','value')
# # )
# # def select_phase(data,option):
# #     if option == None or data == None:
# #         raise PreventUpdate
# #     dictionary = json.loads(data)

# #     match option:
# #         case 'Va':
# #             if dictionary['va_df'] == None:
# #                 return
# #             dff = pd.DataFrame(**(json.loads(dictionary['va_df'])))
# #             va_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
# #             va_plot.update_layout(
# #                 xaxis_title='Hora',
# #                 yaxis_title="Tensão (pu)",
# #                 legend_title="Legenda",
# #                 plot_bgcolor="white",
# #                 font=dict(size=25)
# #                 )
# #             return va_plot
# #         case 'Vb':
# #             if dictionary['vb_df'] == None:
# #                 return
# #             dff = pd.DataFrame(**(json.loads(dictionary['vb_df'])))
# #             vb_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
# #             vb_plot.update_layout(
# #                 xaxis_title='Hora',
# #                 yaxis_title="Tensão (pu)",
# #                 legend_title="Legenda",
# #                 plot_bgcolor="white",
# #                 font=dict(size=25)
# #                 )
# #             return vb_plot
# #         case 'Vc':
# #             if dictionary['vc_df'] == None:
# #                 return
# #             dff = pd.DataFrame(**(json.loads(dictionary['vc_df'])))
# #             vc_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
# #             vc_plot.update_layout(
# #                 xaxis_title='Hora',
# #                 yaxis_title="Tensão (pu)",
# #                 legend_title="Legenda",
# #                 plot_bgcolor="white",
# #                 font=dict(size=25)
# #                 )
# #             return vc_plot
# #         case _:
# #             return None

if __name__ == "__main__":
    app.run(debug=True)
