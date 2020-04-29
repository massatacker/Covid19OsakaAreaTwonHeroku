# -*- coding: utf-8 -*-
import dash  
import dash_core_components as dcc   
import dash_html_components as html
import plotly.graph_objs as go  
import pandas as pd 
import json 

import os

input_area_filename = 'Covid19_Osaka_AreaNumData.xlsx'
input_town_filename = 'Covid19_Osaka_TownNumData.xlsx'
area_town_list_filename = 'OsakaAreaTownList.xlsx'

df_area_num_data = pd.read_excel(input_area_filename)
df_town_num_data = pd.read_excel(input_town_filename)
df_area_town = pd.read_excel(area_town_list_filename)

df_area_twon_initial = df_area_town[ df_area_town['初期値']==1 ]
df_area_twon_initial = df_area_twon_initial.set_index('区域')

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    html.Div([
        html.Div(
            html.H1('大阪府 区域別 市町村別 新型コロナウィルス陽性者数',
            style = {'textAlign': 'center'})
        ),
        html.Div([
            dcc.Dropdown(
                id = 'dropdown-for-area',
                options = [{'label': i, 'value': i} for i in df_area_town['区域'].unique()],
                searchable=False,
                value = '北大阪'
            ),
            dcc.Graph(
                id="area-daily-graph",
            ),
            dcc.Graph(
                id="area-total-graph",
            )
        ], style={
            'display': 'inline-block',
            'width': '49%',
        }),
        html.Div([
            dcc.Dropdown(
                id = 'dropdown-for-town',
                searchable=False,
            ),
            dcc.Graph(
                id="town-daily-graph",
            ),
            dcc.Graph(
                id="town-total-graph",
            )
        ], style={
            'display': 'inline-block',
            'width': '49%',
        })
    ])
])

def create_BarChart(dff, area, sel_deta):
    return {
        'data': [go.Bar(
            x = dff['日付'],
            y = dff[sel_deta]
        )],
        'layout':{
            'title': '{}'.format(sel_deta)
        }
    }

def create_BarScatterChart(dff, area, sel_bar_deta, sel_scatter_data):
    return {
        'data': [go.Bar(
                    x = dff['日付'],
                    y = dff[sel_bar_deta],
                    name = sel_bar_deta),
                 go.Scatter(
                    x = dff['日付'],
                    y = dff[sel_scatter_data],
                    name = sel_scatter_data)
        ],
        'layout':{
            'title': '{}'.format('{}と{}'.format(sel_bar_deta,sel_scatter_data))
        }
    }

@app.callback(
    dash.dependencies.Output('area-daily-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_graph(factor):
    dff = df_area_num_data[df_area_num_data['区域'] == factor]
    return create_BarScatterChart(dff, factor, '日別', '週平均')

@app.callback(
    dash.dependencies.Output('area-total-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_graph(factor):
    dff = df_area_num_data[df_area_num_data['区域'] == factor]
    return create_BarChart(dff, factor, '累計')

@app.callback(
    dash.dependencies.Output('town-daily-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-town', 'value')]
)
def update_graph(factor):
    dff = df_town_num_data[df_town_num_data['市町村'] == factor]
    return create_BarScatterChart(dff, factor, '日別', '週平均')

@app.callback(
    dash.dependencies.Output('town-total-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-town', 'value')]
)
def update_graph(factor):
    dff = df_town_num_data[df_town_num_data['市町村'] == factor]
    return create_BarChart(dff, factor, '累計')

@app.callback(
    dash.dependencies.Output('dropdown-for-town', 'options'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_dropdown_control(factor):
    df_town = df_area_town[df_area_town['区域']==factor]
    return[{'label': i, 'value': i} for i in df_town['市町村'].unique()]

@app.callback(
    dash.dependencies.Output('dropdown-for-town', 'value'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_dropdown_value(factor):
    return df_area_twon_initial.at[factor,'市町村']

if __name__ == '__main__':
    app.run_server(debug=True)
#    app.run_server(debug=True, host='0.0.0.0', port=80)
