import json
from dash import register_page, dcc, html, callback, Output, Input, State, callback_context as ctx
from dash.exceptions import PreventUpdate

import dash_mantine_components as dmc

from src.analysis.iterative import  executar_todas_solucoes_com_fitness

register_page(
    "iterative",
    path="/iterative",
    layout=[
        dmc.Stack(
            children=[
            dmc.Group(
                [
                    dmc.NumberInput(id='max_bess', label='Número máximo de BESS', min=1, max=10),
                    dmc.NumberInput(id='total_power_bess', label='Potência total de BESS', min=1, max=1000, placeholder='Informe a potência total de BESS (será distribuído igualmente entre os BESS)'),
                    dmc.NumberInput(id='total_energy_bess', label='Energia total de BESS', min=1, max=1000, placeholder='Informe a energia total dos BESS'),
                ],
                
            ),
            dmc.Button(
                id='submit-button',
                children='Executar busca analítica',
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
    Output('simulations_select','data'),
    Output('store','data'),
    Input('submit-button','n_clicks'),
    State('max_bess','value'),
    State('total_power_bess','value'),
    State('total_energy_bess','value'),
    prevent_initial_call=True
)
def submit_button_search(n_clicks, max_bess, total_power_bess, total_energy_bess):
    if n_clicks == 0:
        raise PreventUpdate
    
    # Simulação de busca analítica
    if max_bess is None or total_power_bess is None or total_energy_bess is None:
        raise PreventUpdate
    simulations = executar_todas_solucoes_com_fitness()
    # save_json(simulations)
    sim_names = [s['simulation_name'] for s in simulations]
    # Atualiza o estado do componente Store com os dados da simulação
    return sim_names, json.dumps(simulations)

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