from dash import (
    Dash,
    page_container,
    dcc
)
import dash_mantine_components as dmc



app = Dash(__name__,external_stylesheets=dmc.styles.ALL,use_pages=True)
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
        dmc.Flex(
            [ 
                dmc.Box(
                    children=[
                        dmc.NavLink(label="home", href="/", active='exact'),
                        dmc.NavLink(label="indicadores",href='/indicators', active='exact'),
                    ],
                    w="100%",
                    display='flex',
                ),
                dmc.Divider(mb="lg"),
                dmc.Flex(
                    children=[
                        dmc.Title("Simulação", className="menu-title", order=6, w="100%"),
                        dmc.Select(
                            id="simulation-select",
                            data=[],
                            placeholder="Selecione a simulação",
                            disabled=True,
                            maw="800px",
                            w="80%",
                        ),
                        dmc.Button(
                            "Nova simulação",
                            id="new-simulation-button",
                            w="fit-content",
                            n_clicks=0,
                        ),
                    ],
                    direction="row",
                    wrap="wrap",
                    justify="space-between",
                    my="md",
                    mx="md",
                    style={"boxSize": "content-box"},
                ),
                page_container
            ],
            direction="column"),
        dcc.Store(id="simulations"),
        
    ],
    
)








if __name__ == "__main__":
    app.run(debug=True)
