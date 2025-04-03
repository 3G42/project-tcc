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
        dmc.Box([
            dmc.NavLink(label="home", href="/", active='exact'),
            dmc.NavLink(label="indicadores",href='/indicators'),
            dmc.Divider(mb="lg"),
            page_container
        ]),
        dcc.Store(id="simulations"),
        
    ],
    
)








if __name__ == "__main__":
    app.run(debug=True)
