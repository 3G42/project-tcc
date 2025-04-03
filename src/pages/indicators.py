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
    dash_table
    )
import dash_mantine_components as dmc
import pandas as pd
from program import programa
from dash.exceptions import PreventUpdate
import plotly.express as px

register_page(
    "indicadores",
    path="/indicatores",
    layout=[
        
    ]
)