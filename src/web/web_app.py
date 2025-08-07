import sys
from dash import (
    Dash,
    page_container,
    dcc 
)
import dash_mantine_components as dmc


app = Dash(__name__,external_stylesheets=dmc.styles.ALL,use_pages=True,suppress_callback_exceptions=True)
app.layout = dmc.MantineProvider(
    [
        # HEADER
        dmc.Flex(
                    [
                        dmc.Title(
                            children="Simulador de Redes Elétricas",
                            order=1,
                            c="blue.9", # type: ignore
                            
                        ),
                        dmc.Text(
                            "Análise do efeito da geração distribuída e armazenamento em uma rede elétrica de BT",
                            c="gray.8", # type: ignore
                            ta="center",
                            size="lg"
                        ),
                    ],
                    className="header-fluid",
                ),
        dmc.Flex(
            [ 
                dmc.Burger(
                    id='burger-button',
                    opened=False,
                    hiddenFrom='sm'
                ),
                
                ## TODO-1 TERMINAR BOTÃO 
                dmc.Box(
                    children=[
                        dmc.NavLink(label="home", href="/", active='exact'),
                        dmc.NavLink(label="indicadores",href='/indicators', active='exact'),
                        dmc.NavLink(label="iterative",href='/iterative', active='exact'),
                    ],
                    className='nav-bar',
                ),
                dmc.Divider(mb="lg"),
                
                page_container
            ],
            className="container-fluid",
            ),
        dcc.Store(id="simulations", data=dict()),
    ]
    
)

def run_app():
    app.run(debug=True)