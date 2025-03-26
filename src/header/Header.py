from dash import (
    html,
)

def Header():
    return html.Div(
                    [
                        html.H1(
                            children="Simulador de Redes Elétricas",
                            className="header-title",
                        ),
                        html.P(
                            "Análise do efeito de geração distribuída e armazenamento em uma rede elétrica de BT",
                            className="header-description",
                        ),
                    ],
                    className="header",
                ),