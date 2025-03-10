from io import StringIO
import json
from dash import Dash,html,dcc,Input,Output,callback,State,dash_table
import pandas as pd
from dash.exceptions import PreventUpdate

from program import programa
import plotly.express as px

params_storage = ['Barra','Potencia nominal', 'Energia nominal']

app = Dash(__name__)
app.layout = html.Div([
    html.P("Selecione o tipo de análise",style={'margin-bottom':0},),
    dcc.Dropdown(
        id='simulation-dropdown',
        options=[
            {'value':'start-case','label':'Sem GD e Baterias',},
            {'value':'without-storage', 'label':'Sem armazenamento'},
            {'value':'with-gd-storage', 'label':'Com GD e Baterias'},
        ],
        placeholder="Selecione o tipo de simulação",
        value=None,
        clearable=False,
    ),
    html.Div(id='storages-form-container',children=[
        html.P('Barra',style={'margin-bottom':0}),
        dcc.Dropdown(
            id='bar-dropdown',
            options=[{'label':f'Barra {i}','value':i} for i in range(1,15)],
            value=None,
            clearable=False,
        ),
        html.P('Potência Nominal(kW)',style={'margin-bottom':0}),
        dcc.Input(
            id='power-input',
            type='number',
            value=None,
            placeholder='Potencia nominal',
        ),
        html.P('Energia Nominal(kWh)',style={'margin-bottom':0}),
        dcc.Input(
            id='energy-input',
            type='number',
            value=None,
            placeholder='Energia Nominal',
        ),
        html.Button('Adicionar',id='editing-rows-button',n_clicks=0,disabled=False),
    ], style={'display':'none'}),
    html.Div(id='table-container', children=[
        dash_table.DataTable(
            id='table-editing-simple',
            columns=([{'id':p, 'name':p} for p in params_storage]),
            data=[],
            editable=True,
        ),
        html.Button('Salvar',id='save-button',n_clicks=0)
    ], style={'display':'none'}),
    dcc.Dropdown(
        id='graph-dropdown',
        options={'V':'Tensão','P':'Potência','E':'Energia'},
        value=None,
        clearable=False,
        disabled=True
        ),
    dcc.RadioItems(
        id='graph-select',
        style={'display':'none'},
        options=[],
        inline=True,
        ),

    
    dcc.Checklist(
        id='bus-select',
        options=[{'label':f'Barra {i}','value':i} for i in range(1,15)],
        value=[],
        style={'display':'none'},
        inline=True,),
    
    dcc.Graph(id='graph'),
    
    
    
    dcc.Store(id='simulations')
    ], style={'display':'flex','flex-direction':'column','align-items':'stretch','justify-content':'space-between','padding': 10,'width':'100%','gap':10}
    )


@callback(
    Output('simulations','data'),
    Output('graph-dropdown', 'disabled'),
    Output('graph-dropdown', 'options'),
    Output('graph-dropdown', 'value'),
    Input('simulation-dropdown','value'),
    Input('save-button','n_clicks'),
    State('table-editing-simple','data'),
    State('simulations','data'),

    prevent_initial_call=True
)
def select_simulation(sim,n_clicks,storages_data,previous_data,):
    if sim is None:
        return None,True,None,None
    else:   
        if previous_data is None:
            previous = {}
        else:
            previous = json.loads(previous_data)
            if sim in previous:
                return previous_data,False,{'V':'Tensão','P':'Potência','E':'Energia'},None
        if sim == 'with-gd-storage':
            json_data = programa(sim,storages_data)   
        else:
            json_data = programa(sim)
        previous[sim] = json_data
        data = json.dumps(previous)
        return data,False,{'V':'Tensão','P':'Potência','E':'Energia'},None



@callback(
    Output('graph-select','style'),
    Output('graph-select','options'),
    Input('graph-dropdown','value'),
    prevent_initial_call=True
)
def select_graph(val):
    if val is None:
        raise PreventUpdate
    match val:
        case 'V':
            return {'display':'block'},[
                {'label':'Fase A','value':'va'},
                {'label':'Fase B','value':'vb'},
                {'label':'Fase C','value':'vc'}
            ]
        case 'P':
            return {'display':'block'},[
                {'label':'Fase A','value':'pa'},
                {'label':'Fase B','value':'pb'},
                {'label':'Fase C','value':'pc'},
                {'label':'Neutro','value':'p0'}
            ]



@callback(
    Output('graph', 'figure'),
    Input('graph-select','value'),
    State('simulations','data'),
    State('simulation-dropdown','value'),
    prevent_initial_call=True
)
def select_graph_type(val,data,sim):
    if val is None or data is None:
        raise PreventUpdate
    store = json.loads(data)
    dictionary = store[sim]
    match val:
        case 'va'|'vb'|'vc':
            dff = pd.DataFrame(**(json.loads(dictionary[val])))
            v_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
            v_plot.update_layout(
                xaxis_title='Hora',
                yaxis_title="Tensão (pu)",
                legend_title="Legenda",
                plot_bgcolor="white",
                font=dict(size=25)
                )
            return v_plot
        case 'pa'|'pb'|'pc'|'p0':
            dff = pd.DataFrame(**(json.loads(dictionary[val])))
            p_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
            p_plot.update_layout(
                xaxis_title='Hora',
                yaxis_title="Potência (pu)",
                legend_title="Legenda",
                plot_bgcolor="white",
                font=dict(size=25)
                )
            return p_plot
        case _:
            return None



@callback(
    Output('storages-form-container','style',allow_duplicate=True),
    Input('simulation-dropdown','value'),
    prevent_initial_call=True,
)
def show_storage(val):
    if val == 'with-gd-storage':
        return {'display':'block','padding': 10}
    else:
        return {'display':'none','padding': 10}

@callback(
    Output('table-editing-simple','data'),
    Input('editing-rows-button','n_clicks'), 
    State('bar-dropdown','value'),
    State('power-input','value'),
    State('energy-input','value'),
    State('table-editing-simple','data'),
    State('table-editing-simple','columns')
)
def add_row(n_clicks,bar,power,energy,data,columns):
    if n_clicks>0:
        data.append({
            'Barra':bar,
            'Potencia nominal':power,
            'Energia nominal':energy
        })
    return data

@callback(
    Output('table-container','style'),
    Input('editing-rows-button','n_clicks'),
    prevent_initial_call=True
)
def show_table(n_clicks):
    if n_clicks>0:
        return {'display':'block'}
    else:
        return {'display':'none'}
    

@callback(
    Output('table-editing-simple','editable'),
    Output('editing-rows-button','disabled'),
    Output('storages-form-container','style',allow_duplicate=True),
    Output('save-button','style'),
    Input('save-button','n_clicks'),
    State('table-editing-simple','data'),
    prevent_initial_call=True
)
def update_storage(n_clicks,data):
    if data == []:
        return True,False,{'display':'block'},{'display':'block'}
    if n_clicks>0:
        
        return False,True,{'display':'none'},{'display':'none'}
    return True,False,{'display':'block'},{'display':'block'}



# @callback(
#     Output('graph-dropdown', 'disabled'),
#     State('simulation-dropdown','value'),
    
# )

# @callback(
#     Output('intermediate-value','data'),
#     Input('dropdown-1','value'),   
    
# )
# def select_graph_type(val):
#     if val is None:
#         # PreventUpdate prevents ALL outputs updating
#         raise PreventUpdate
#     ## Quero converter a pd.Series de Dataframes, para um json
#     json_data = programa()
    
#     json_data = json.dumps(json_data)
#     print(json_data)
#     return json_data
    
    

# @callback(
#     Output('graph', 'figure'), 
#     Input('intermediate-value', 'data'),
#     Input('dropdown-2','value')
# )
# def select_phase(data,option):
#     if option == None or data == None:
#         raise PreventUpdate
#     dictionary = json.loads(data)

#     match option:
#         case 'Va':
#             if dictionary['va_df'] == None:
#                 return 
#             dff = pd.DataFrame(**(json.loads(dictionary['va_df'])))
#             va_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
#             va_plot.update_layout(
#                 xaxis_title='Hora',
#                 yaxis_title="Tensão (pu)",
#                 legend_title="Legenda",
#                 plot_bgcolor="white",
#                 font=dict(size=25)
#                 )
#             return va_plot
#         case 'Vb':
#             if dictionary['vb_df'] == None:
#                 return 
#             dff = pd.DataFrame(**(json.loads(dictionary['vb_df'])))
#             vb_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
#             vb_plot.update_layout(
#                 xaxis_title='Hora',
#                 yaxis_title="Tensão (pu)",
#                 legend_title="Legenda",
#                 plot_bgcolor="white",
#                 font=dict(size=25)
#                 )
#             return vb_plot
#         case 'Vc':
#             if dictionary['vc_df'] == None:
#                 return 
#             dff = pd.DataFrame(**(json.loads(dictionary['vc_df'])))
#             vc_plot = px.line(dff,x=dff.index,y=dff.columns[0:])
#             vc_plot.update_layout(
#                 xaxis_title='Hora',
#                 yaxis_title="Tensão (pu)",
#                 legend_title="Legenda",
#                 plot_bgcolor="white",
#                 font=dict(size=25)
#                 )
#             return vc_plot
#         case _:
#             return None

if __name__ == "__main__":
    app.run(debug=True)