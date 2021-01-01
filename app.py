# -*- coding: utf-8 -*-
import dash  
import dash_core_components as dcc   
import dash_html_components as html
import plotly.graph_objs as go  
import pandas as pd 

import os

input_area_filename = 'Covid19_Osaka_Area2NumData.xlsx'
input_town_filename = 'Covid19_Osaka_TownNumData.xlsx'
area_town_list_filename = 'OsakaArea2TownList.xlsx'

df_area_num_data = pd.read_excel(input_area_filename)
df_town_num_data = pd.read_excel(input_town_filename)
df_area_town = pd.read_excel(area_town_list_filename)

df_area_twon_initial = df_area_town[ df_area_town['初期値']==1 ]
df_area_twon_initial = df_area_twon_initial.set_index('地域')

last_update = df_town_num_data.iloc[-1]['日付']

osaka_color = '#364C97'
light_color = '#1E90FF'
comment_color = '#C0C0C0'
update_color = '#777777'

title_str = '大阪府 地域別 市町村別 新型コロナウィルス陽性者数'
discharge_comment = '※退院には死亡退院を含む'

app = dash.Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "google-site-verification", "content": "VnMLuf8OB37rHc2zxfWBWZO3PC86241f75o6OsIgK_4"}
    ]
)
app.title = title_str

server = app.server

app.layout = html.Div(children=[
    html.Div([
        html.Div([
            html.H1(title_str,
            style = {'textAlign': 'center','margin-bottom':'0%'}),
            html.Div([
                #html.H4(f'{last_update.date()}更新',
                html.H4('{}更新'.format(last_update.strftime('%Y/%m/%d')),
                style = {'margin':'0%', 'color':update_color}),
                html.A('出典:covid19-osaka.info',
                href = 'https://covid19-osaka.info/'),
            ],
            style={'textAlign':'right','margin-bottom':'1%','margin-right':'2%'}),
        ]),
        html.Div([
            dcc.Dropdown(
                id = 'dropdown-for-area',
                options = [{'label': i, 'value': i} for i in df_area_town['地域'].unique()],
                searchable=False,
                clearable=False,
                value = '豊能'
            ),
            dcc.Graph(
                id="area-daily-graph",
                #config = {'staticPlot': True},
            ),
            dcc.Graph(
                id="area-total-graph",
                #config = {'staticPlot': True},
            ),
            #html.H5(discharge_comment,
            #style = {'color':comment_color})
        ],
        style={"verticalAlign": "top"},
        className='graph_box',
        ),
        html.Div([
            dcc.Dropdown(
                id = 'dropdown-for-town',
                searchable=False,
                clearable=False,
            ),
            dcc.Graph(
                id="town-daily-graph",
                #config = {'staticPlot': True},
            ),
            dcc.Graph(
                id="town-total-graph",
                #config = {'staticPlot': True},
            ),
            #html.H5(discharge_comment,
            #style = {'color':comment_color})
        ],
        style={"verticalAlign": "top"},        
        className='graph_box',
        ),
    ])
])

def create_2BarChart(dff, area, bar1_data, bar1_name, bar2_data, bar2_name, title):
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
            'margin':{'l':30, 'r':20, 't':100, 'b':30},
            'legend':{"x":0.85, "y":1.15},
            'title': '{} {}'.format(area, title),
            'barmode':'group',
            'bargroupgap':0.0,
            'xaxis':{'fixedrange':True, 'tickformat':'%_m/%-d'},
            'yaxis':{'fixedrange':True},
            #'bargap':0.2,
        },
    }

def create_1BarChart(dff, area, bar1_data, bar1_name, title):
    return {
        'data': [go.Bar(
                    x = dff['日付'],
                    y = dff[bar1_data],
                    name = bar1_name,
                    marker_color = osaka_color),
                  #go.Bar(
                  #  x = dff['日付'],
                  #  y = dff[bar2_data],
                  #  name = bar2_name,
                  #  marker_color = light_color)
                  ],
        'layout':{
            'margin':{'l':30, 'r':20, 't':100, 'b':30},
            'legend':{"x":0.85, "y":1.15},
            'title': '{} {}'.format(area, title),
            'barmode':'group',
            'bargroupgap':0.0,
            'xaxis':{'fixedrange':True, 'tickformat':'%_m/%-d'},
            'yaxis':{'fixedrange':True},
            #'bargap':0.2,
        },
    }

def create_BarScatterChart(dff, area, bar_data, bar_name, scatter_data, scatter_name, title):
    return {
        'data': [go.Bar(
                    x = dff['日付'],
                    y = dff[bar_data],
                    name = bar_name,
                    marker_color = osaka_color),
                 go.Scatter(
                    x = dff['日付'],
                    y = dff[scatter_data],
                    name = scatter_name,
                    line = dict(color = light_color, width = 4))
        ],
        'layout':{
            'margin':{'l':30, 'r':20, 't':100, 'b':30},
            'legend':{"x":0.85, "y":1.15},
            'title': '{} {}'.format(area, title),
            'xaxis':{'fixedrange':True, 'tickformat':'%_m/%-d'},
            'yaxis':{'fixedrange':True},
        }
    }

@app.callback(
    dash.dependencies.Output('area-daily-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_graph(factor):
    dff = df_area_num_data[df_area_num_data['地域'] == factor]
    return create_BarScatterChart(dff, factor, '日別', '日別', '週平均', '7日平均', '陽性者')

@app.callback(
    dash.dependencies.Output('area-total-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_graph(factor):
    dff = df_area_num_data[df_area_num_data['地域'] == factor]
    return create_1BarChart(dff, factor, '累計', '陽性', '累計')
    #return create_2BarChart(dff, factor, '累計', '陽性', '退院・解除累計', '退院', '累計')

@app.callback(
    dash.dependencies.Output('town-daily-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-town', 'value')]
)
def update_graph(factor):
    dff = df_town_num_data[df_town_num_data['市町村'] == factor]
    return create_BarScatterChart(dff, factor, '日別', '日別', '週平均', '7日平均', '陽性者')

@app.callback(
    dash.dependencies.Output('town-total-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-town', 'value')]
)
def update_graph(factor):
    dff = df_town_num_data[df_town_num_data['市町村'] == factor]
    return create_1BarChart(dff, factor, '累計', '陽性', '累計')
    #return create_2BarChart(dff, factor, '累計', '陽性', '退院・解除累計', '退院', '累計')

@app.callback(
    dash.dependencies.Output('dropdown-for-town', 'options'),
    [dash.dependencies.Input('dropdown-for-area', 'value')]
)
def update_dropdown_control(factor):
    df_town = df_area_town[df_area_town['地域']==factor]
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
