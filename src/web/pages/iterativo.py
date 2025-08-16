import json
from dash import register_page, dcc, html, callback, Output, Input, State, callback_context as ctx
from dash.exceptions import PreventUpdate

import dash_mantine_components as dmc

from src.analysis.iterative import executar_todas_solucoes_com_fitness
from src.simulation.GA import rodar_ga


values_types = [
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



register_page(
    "iterative",
    path="/iterative",
    layout=[
        dmc.Stack(
            children=[
            dmc.Group(
                [
                    dmc.NumberInput(id='qtt_bess', label='Quantidade de BESS', min=2, max=10),
                    dmc.NumberInput(id='total_power_bess', label='Potência total de BESS', min=1, max=1000, placeholder='Informe a potência total de BESS'),
                    dmc.NumberInput(id='total_energy_bess', label='Energia total de BESS', min=1, max=1000, placeholder='Informe a energia total dos BESS'),
                    dmc.NumberInput(id='generations-input', label='Quantidade de gerações da GA', min=10, max=200, placeholder='Informe a quantidade gerações'),
                    dmc.NumberInput(id='population-size-input', label='Quantidade de individuos por geração', min=6, max=50,
                                    placeholder='Informe a quantidade individuos por geração')

                ],
                
            ),
            dmc.Button(
                id='submit-button',
                children='Executar busca com GA',
                n_clicks=0,
                color='blue',
                variant='outline',
                size='lg',
                radius='md',
                className='button-submit'
            ),
            dmc.LoadingOverlay(
                id='loading-overlay',
                loaderProps={'color': 'blue.9'},
                className='loading-overlay'
            ),
            dmc.Group(id="visualization-container", children=[
                dmc.Stack(
                    children=[
                        dmc.Select(
                            id="value-select",
                            label="Selecione as variáveis a serem monitoradas",
                            value=[],  # type: ignore
                            data=values_types,  # type: ignore
                            disabled=True,
                            maw="800px",
                            w="80%",
                            mx="md",
                        ),
                        dmc.Tree(data=[], checkboxes=True, id='tree-checkboxes')

                    ]
                )

            ]),
            dmc.Select(
                id='simulations_select',
                label='Simulações',
                placeholder='Selecione uma simulação',
                data=[],
                searchable=True,
                clearable=True,
                style={'width': '100%'},
            ),
                dcc.Graph(id="graph_iterative", style={"display": "none"}),
                dcc.Store(
                    id='store',
                    data=json.dumps({}),
                    storage_type='session'
                ),]
        ),
    ]
)
@callback(
    Output("simulation-select", "data"),
    Output("simulation-select", "disabled"),
    Output("value-select", "disabled"),
    Input("simulations", "data"),
    prevent_initial_call=True,
)
def update_simulation_select(data):
    if data is None:
        return [], True, True
    options = []
    for k in data.keys():
        options = options + [{"label": k, "value": k}]
    return options, False, False


@callback(
    Output('','data'),
    Output('store','data'),
    Input('submit-button','n_clicks'),
    State('qtt_bess','value'),
    State('total_power_bess','value'),
    State('total_energy_bess', 'value'),
    State('generations-input','value'),
    State('population-size-input', 'value'),

    prevent_initial_call=True
)
def submit_button_search(n_clicks, qtt_bess, total_power_bess, total_energy_bess,gen,pop_size):
    if n_clicks == 0:
        raise PreventUpdate
    
    # Simulação de busca analítica
    if qtt_bess is None or total_power_bess is None or total_energy_bess is None or gen is None or pop_size is None:
        raise PreventUpdate
    simulations = rodar_ga(N_BATERIAS=qtt_bess, P_TOTAL_MAX=total_power_bess,E_TOTAL_MAX=total_energy_bess,POP_SIZE=pop_size,GERACOES=gen)

    generations_names = [f'Gen:{idx}-{simulations[idx][0]} 'for idx in range(len(simulations))]

    for simulations
    # save_json(simulations)
    # Atualiza o estado do componente Store com os dados da simulação
    return generations_names, json.dumps(simulations)

# @callback(
#     Output("graph_iterative", "style"),
#     Output("graph_iterative", "figure"),
#     Input("simulations_select", "value"),
#     State("store", "data"),
#     prevent_initial_call=True,
# )
# def select_graph(value,data):
#     if simul is None or data is None:
#         raise PreventUpdate
#     obj = json.loads(data)

#     simulation_data = obj[simulation]
#     if simulation_data is None or value is None:
#         raise PreventUpdate

#     df = pd.DataFrame(**(json.loads(simulation_data[value])))
#     if df.empty:
#         raise PreventUpdate
    
#     print(simulation_data['id'])
#     print(f'Feeder Losses: {simulation_data['feeder_losses']}')
#     print(f'Feeder Energy: {simulation_data['feeder_energy']}')

#     fig = px.line(df, x=df.index, y=df.columns)
#     fig.update_layout(
#         xaxis_title="Hora",
#         yaxis_title=f"{'Tensão' if value == "va" or value=='vb'or value =='vc' else 'Potência'} (pu)",
#         legend_title=f"{'Tensão' if value == "va" or value=='vb' or value =='vc' else 'Potência'}",
#         plot_bgcolor="white",
#         font=dict(size=25),
#     )
#     return {"display": "block"}, fig

# def save_json(data):
#     with open("data.json", "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)