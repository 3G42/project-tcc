        html.Div(
            [  # Header
                
                html.Div(
                    children=[
                        html.H4(
                            children="Simulação",
                            className='menu-title',
                        ),
                        dcc.Dropdown(
                            id="simulation-select",
                            options=[
                                {
                                    "value": "start-case",
                                    "label": "Sem GD e Baterias",
                                },
                                {
                                    "value": "without-storage",
                                    "label": "Sem armazenamento",
                                },
                                {
                                    "value": "with-gd-storage",
                                    "label": "Com GD e Baterias",
                                },
                            ],
                            value=None,
                            className="dropdown",
                            
                        ),
                    ],
                ),
                html.Div(
                    id="storages-container",
                    children=[
                        html.Div(
                            id="storages-form-container",
                            className="form-container disabled",
                            children=[
                                html.P("Barra", style={"marginBottom": 0}),
                                dcc.Input(
                                    id="bar-number",
                                    type="number",
                                    value=None,
                                ),
                                html.P(
                                    "Potência Nominal(kW)", style={"marginBottom": 0}
                                ),
                                dcc.Input(
                                    id="power-input",
                                    type="number",
                                    value=None,
                                    placeholder="Potencia nominal",
                                ),
                                html.P(
                                    "Energia Nominal(kWh)", style={"marginBottom": 0}
                                ),
                                dcc.Input(
                                    id="energy-input",
                                    type="number",
                                    value=None,
                                    placeholder="Energia Nominal",
                                ),
                                html.Button(
                                    "Adicionar",
                                    id="editing-rows-button",
                                    n_clicks=0,
                                    disabled=False,
                                ),
                            ],
                            style={
                                "border": "1px solid gray",
                                "width": "fit-content",
                                "paddingTop": 0,
                                "paddingBottom": 10,
                                "paddingLeft": 10,
                                "paddingRight": 10,
                                "marginRight": 16,
                                "marginLeft": 36,
                                "height": 180,
                            },
                        ),
                        html.Div(
                            id="table-container",
                            children=[
                                dash_table.DataTable(
                                    id="table-editing-simple",
                                    columns=(
                                        [{"id": p, "name": p} for p in params_storage]
                                    ),
                                    data=[],
                                    editable=True,
                                    style_table={"height": 180, "overflowY": "auto"},
                                ),
                                html.Button("Salvar", id="save-button", n_clicks=0),
                            ],
                            style={"display": "none"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "alignItems": "flex-start",
                        "justifyContent": "flex-start",
                        "padding": 10,
                        "gap": 10,
                    },
                ),
                html.Span(
                    children=[
                        html.H4(
                            "Selecione a variável",
                            style={"textAlign": "center", "fontSize": "18px"},
                        ),
                        dcc.RadioItems(
                            id="graph-dropdown",
                            options={"V": "Tensão", "P": "Potência"},
                            value=None,
                            inline=True,
                            style={"display": "flex", "justifyContent": "space-around"},
                        ),
                    ],
                    style={
                        "display": "grid",
                        "gap": 20,
                        "gridTemplateColumns": "1fr 2fr 3fr",
                        "alignItems": "center",
                    },
                ),
                html.Span(
                    children=[
                        html.H4(
                            "Selecione o condutor/fase",
                            style={"textAlign": "center", "fontSize": "18px"},
                        ),
                        dcc.RadioItems(
                            id="graph-select",
                            style={"display": "none"},
                            options=[],
                            inline=True,
                        ),
                    ],
                    style={
                        "display": "grid",
                        "gap": 20,
                        "gridTemplateColumns": "1fr 2fr 3fr",
                        "alignItems": "center",
                    },
                ),
                dcc.Checklist(
                    id="bus-select",
                    options=[{"label": f"Barra {i}", "value": i} for i in range(1, 15)],
                    value=[],
                    inline=True,
                ),
            ],
        ),