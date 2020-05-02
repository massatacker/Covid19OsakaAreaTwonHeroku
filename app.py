# -*- coding: utf-8 -*-
import dash  
import dash_core_components as dcc   
import dash_html_components as html
import plotly.graph_objs as go  
import pandas as pd 

import os

input_area_filename = 'Covid19_Osaka_AreaNumData.xlsx'
input_town_filename = 'Covid19_Osaka_TownNumData.xlsx'
area_town_list_filename = 'OsakaAreaTownList.xlsx'

df_area_num_data = pd.read_excel(input_area_filename)
df_town_num_data = pd.read_excel(input_town_filename)
df_area_town = pd.read_excel(area_town_list_filename)

df_area_twon_initial = df_area_town[ df_area_town['初期値']==1 ]
df_area_twon_initial = df_area_twon_initial.set_index('区域')

osaka_color = '#364C97'
light_color = '#1E90FF'

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


def create_2BarChart(dff, bar1_data, bar1_name, bar2_data, bar2_name, title):
    return {
        'data': [go.Bar(
                    x = dff['日付'],
                    y = dff[bar1_data],
                    name = bar1_name,
                    marker_color = osaka_color),
                  go.Bar(
                    x = dff['日付'],
                    y = dff[bar2_data],
                    name = bar2_name,
                    marker_color = light_color)
        ],
        'layout':{
            'title': '{}'.format(title),
            'barmode':'group',
            'bargroupgap':0.0,
            #'bargap':0.2,
        }
    }

def create_BarScatterChart(dff, bar_data, bar_name, scatter_data, scatter_name, title):
    return {
        'data': [go.Bar(
                    x = dff['日付'],
                    y = dff[bar_data],
                    name = bar_name,
                    marker_color = osaka_color),
                    #marker = dict(color = osaka_color)),
                 go.Scatter(
                    x = dff['日付'],
                    y = dff[scatter_data],
                    name = scatter_name,
                    line = dict(color = light_color, width = 4))
        ],
        'layout':{
            'title': '{}'.format('{}'.format(title))
        }
    }

@app.callback(
    dash.dependencies.Output('area-daily-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_graph(factor):
    dff = df_area_num_data[df_area_num_data['区域'] == factor]
    return create_BarScatterChart(dff, '日別', '日別', '週平均', '週平均', '陽性者')

@app.callback(
    dash.dependencies.Output('area-total-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_graph(factor):
    dff = df_area_num_data[df_area_num_data['区域'] == factor]
    return create_2BarChart(dff, '累計', '陽性', '退院・解除累計', '退院', '累計')

@app.callback(
    dash.dependencies.Output('town-daily-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-town', 'value')]
)
def update_graph(factor):
    dff = df_town_num_data[df_town_num_data['市町村'] == factor]
    return create_BarScatterChart(dff, '日別', '日別', '週平均', '週平均', '陽性者')

@app.callback(
    dash.dependencies.Output('town-total-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-town', 'value')]
)
def update_graph(factor):
    dff = df_town_num_data[df_town_num_data['市町村'] == factor]
    return create_2BarChart(dff, '累計', '陽性', '退院・解除累計', '退院', '累計')

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
