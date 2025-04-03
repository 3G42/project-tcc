from dash import register_page, dcc, html, callback, Output, Input, State, callback_context as ctx
from dash.exceptions import PreventUpdate

import dash_mantine_components as dmc

from analysis.iterative import iterative_search

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
            )]
        ),
        dcc.Store(id='simulations_iterative'),
    ]
)

@callback(
    Output('simulations_iterative','data'),
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
    simulations = iterative_search(max_bess, total_power_bess, total_energy_bess)
    
    # Atualiza o estado do componente Store com os dados da simulação
    return simulations