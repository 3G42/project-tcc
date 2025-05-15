import json
from typing import Dict, List, Union
from dash import (
    dcc,
    Input,
    Output,
    callback,
    State,
    callback_context,
    register_page,
    dash_table,
    html,
)
from dash.dash_table.Format import Format, Scheme, Trim, Align
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
from dash.exceptions import PreventUpdate
import plotly.express as px




def truncate_value(x):
    return np.round(x, decimals=3)


register_page(
    "indicadores",
    path="/indicators",
    layout=[
        dmc.Flex(
            id="general-indicators",
            children=[
                dmc.Title(
                    children="Indicadores gerais",
                    order=3,
                    c="blue",
                ),
                dmc.Flex(
                    children=[
                        dmc.Stack(
                            id="indicators-chip-group",
                            w="fit-content",
                            px="sm",
                            align="flex-start",
                            justify="flex-start",
                        ),
                        dmc.Group(id="indicators-container", children=[]),
                    ],
                    direction="row",
                ),
            ],
            mx="lg",
            direction="column",
            align="flex-start",
            justify="space-evenly",
            gap="md",
            pt="lg",
            pb="md",
        ),
    ],
)


@callback(
    Output("indicators-container", "children"),
    Input(
        "chip-group",
        "value",
    ),
    State("simulations", "data"),
)
def update_datatable(value, data):
    if data is None or value is None or value == []:
        raise PreventUpdate

    obj: Dict = json.loads(data)

    keys_arr = list(obj.keys())

    selected_key = value

    df = obj[selected_key]["v_indicators"]
    df = pd.DataFrame(**(json.loads(df)))
    df = df.transpose()
    df = df.apply(truncate_value)
    print(df)
    df = df.reset_index().rename(columns={"index": "barra"})
    columns = [
        {
            "name": col,
            "id": col,
            "type": "numeric",
            "format": Format(precision=2, scheme=Scheme.fixed, align=Align.right),
        }
        for col in df.columns
    ]
    data = [{col: val for col, val in row.items()} for row in df.to_dict("records")]  # type: ignore

    return (
        dash_table.DataTable(
            id="general-indicators-table",
            columns=columns,
            data=data,
            style_table={"overflowX": "auto", "maxWidth": "64em"},
            style_cell={
                "padding": "5px",
                "width": "120px",
            },
            style_header={
                "backgroundColor": "#f1f1f1",
                "fontWeight": "bold",
                "textAlign": "center",
            },
            merge_duplicate_headers=True,
            style_data_conditional=[
                {
                    "if": {
                        "filter_query": "{{{}}} > 3".format(coluna),
                        "column_id": coluna,
                    },
                    "backgroundColor": "tomato",
                }
                for coluna in ["DRP_A", "DRP_B", "DRP_C"]
            ]
            + [
                {
                    "if": {
                        "filter_query": "{{{}}} > 0.5".format(coluna),
                        "column_id": coluna,
                    },
                    "backgroundColor": "red",
                }
                for coluna in ["DRC_A", "DRC_B", "DRC_C"]
            ],
        ),
    )

    # for i in range(len(keys_arr)):
    #     if keys_arr[i] not in selected_keys:
    #         pass
    #     else:
    #         ind = pd.DataFrame(**(json.loads(obj[keys_arr[i]]['v_indicators'])))
    #         ind = ind.transpose()
    #         ind = ind.apply(truncate_value)
    #         drp_a[f'{i+1}'] = ind['DRP_A']
    #         drp_b[f'{i+1}'] = ind['DRP_B']
    #         drp_c[f'{i+1}'] = ind['DRP_C']
    #         drc_a[f'{i+1}'] = ind['DRC_A']
    #         drc_b[f'{i+1}'] = ind['DRC_B']
    #         drc_c[f'{i+1}'] = ind['DRC_C']
    #         print(drp_a)

    # drp_a = pd.concat(drp_a, keys=drp_a.keys(),axis=1)
    # drp_b = pd.concat(drp_b, keys=drp_b.keys(),axis=1)
    # drp_c = pd.concat(drp_c, keys=drp_c.keys(),axis=1)
    # drc_a = pd.concat(drc_a, keys=drc_a.keys(),axis=1)
    # drc_b = pd.concat(drc_b, keys=drc_b.keys(),axis=1)
    # drc_c = pd.concat(drc_c, keys=drc_c.keys(),axis=1)

    # df = pd.concat([drp_a, drp_b, drp_c, drc_a, drc_b, drc_c], axis=1, keys=['DRP_A', 'DRP_B', 'DRP_C', 'DRC_A', 'DRC_B', 'DRC_C'])
    # df = df.reset_index().rename(columns={'index':'barra'})
    # print(df)
    # columns = [{"name": col, "id": "_".join(col),'type':'numeric','format':Format(precision=2, scheme=Scheme.fixed, align=Align.right)} for col in df.columns]
    # data = [{"_".join(col): val for col, val in row.items() } for row in df.to_dict('records')] # type: ignore
    # return columns,data
    # indicators = {f'{i+1}': pd.DataFrame(**(json.loads(obj[keys_arr[i]]['v_indicators']))) for i in range(len(keys_arr)) if keys_arr[i] in selected_keys}

    # indicators = pd.concat(indicators, keys=indicators.keys())
    # df = indicators.transpose()
    # print(df)
    # df = df.apply(truncate_value)
    # df = df.reset_index().rename(columns={'index':'barra'})
    # columns = [{"name": col, "id": "_".join(col)} for col in df.columns]
    # data = [{"_".join(col): val for col, val in row.items() } for row in df.to_dict('records')] # type: ignore

    return [], []


@callback(Output("indicators-chip-group", "children"), Input("simulations", "data"))
def get_indicators_group(data):
    if data is None:
        raise PreventUpdate

    obj: Dict = json.loads(data)
    keys_arr = list(obj.keys())
    chips = (
        dmc.ChipGroup(
            children=[
                dmc.Chip(
                    f"{keys_arr[i]}",
                    value=f"{keys_arr[i]}",
                    id=f"chip-{i}",
                    styles={"textWrap": "wrap"},
                )
                for i in range(len(keys_arr))
            ],
            id="chip-group",
            value=None,
        ),
    )

    return chips
