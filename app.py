# -*- coding: utf-8 -*-
import dash  
import dash_core_components as dcc   
import dash_html_components as html
import plotly.graph_objs as go  
import pandas as pd 
import numpy as np
import datetime
import os

input_area_filename = 'Covid19_Osaka_Area2NumPopuData.xlsx'
input_town_filename = 'Covid19_Osaka_TownNumPopuData.xlsx'
area_town_list_filename = 'OsakaArea2TownList.xlsx'

df_area_num_data = pd.read_excel(input_area_filename)
df_town_num_data = pd.read_excel(input_town_filename)
df_area_town = pd.read_excel(area_town_list_filename)

df_area_twon_initial = df_area_town[ df_area_town['初期値']==1 ]
df_area_twon_initial = df_area_twon_initial.set_index('地域')

last_update = df_town_num_data.iloc[-1]['日付']

osaka_color = '#364C97'
light_color = '#1E90FF' # dodgerblue
comment_color = '#C0C0C0' # silver
update_color = '#777777'
center_color = '#FFA500' # orange
inc_color = '#FF4500' # orangered
dec_color = '#32CD32' # limegreen
center_text_color = '#D2691E' #chocolate
inc_text_color = '#DC143C' # crimson #'#8B0000' # darkred
dec_text_color = '#228B22' # forestgreen #'#006400' # darkgreen

title_str = '大阪府 地域別 市町村別 新型コロナウイルス陽性者数'
discharge_comment = '※退院には死亡退院を含む'

inc_dec_start_date = datetime.datetime(2022, 3, 20)
#inc_dec_start_date = datetime.datetime(2022, 1, 1)
#inc_dec_start_date = datetime.datetime(2021, 7, 1)

td_12h = datetime.timedelta(hours=12)
graph_min_date = df_town_num_data.iloc[0]['日付'] + td_12h
graph_max_date = last_update + td_12h
graph_start_date = inc_dec_start_date + td_12h


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
                html.Div([
                    html.A('出典:大阪府/新型コロナウイルス感染症患者の発生状況について',
                            href = 'https://www.pref.osaka.lg.jp/iryo/osakakansensho/happyo.html',
                            style = {'margin':'0%'})
                ]),
                html.Div([
                    html.A('出典:大阪市/感染症・病気に関すること',
                            href = 'https://www.city.osaka.lg.jp/kenko/page/0000502869.html',
                            style = {'margin':'0%'})
                ]),
            ],
            style={'textAlign':'right','margin-bottom':'0%','margin-right':'2%'}),
            html.Div([
            html.Div([
                dcc.RadioItems(
                    id = 'radio_inc_ratio_persons',
                    options=[
                        {'label': '増加比率', 'value': 'inc_ratio'},
                        {'label': '陽性者数', 'value': 'persons'},
                    ],
                    value='inc_ratio',
                    labelStyle={'margin-left':'1%','margin-right':'1%'},
                    ),
            ],
            style={'textAlign':'center','margin-bottom':'1%'}),
                dcc.RadioItems(
                    id = 'radio_real_per_popu',
                    options=[
                        {'label': '実数', 'value': 'real_persons'},
                        {'label': '人口10万人当り', 'value': 'per_popu_ht'},
                    ],
                    value='real_persons',
                    labelStyle={'margin-left':'1%','margin-right':'1%'},
                    ),
            ],
            style={'textAlign':'center','margin-bottom':'1%'}),
            html.Div([
                dcc.RangeSlider(
                    id = 'slider_range_date',
                    min = graph_min_date.timestamp(),
                    max = graph_max_date.timestamp(),
                    value = [graph_start_date.timestamp(), graph_max_date.timestamp()],
            ),
            html.Div(
                id='slider-container',
                style={'textAlign':'center'})
            ],
            ),
        ]),
        html.Div([
            dcc.Dropdown(
                id = 'dropdown-for-area',
                options = [{'label': i, 'value': i} for i in df_area_town['地域'].unique()],
                searchable=False,
                clearable=False,
                value = '全域',
                #value = '豊能',
            ),
            dcc.Graph(
                id="area-graph",
                #config = {'staticPlot': True},
            ),
            #dcc.Graph(
            #    id="area-daily-graph",
            #    #config = {'staticPlot': True},
            #),
            #dcc.Graph(
            #    id="area-total-graph",
            #    #config = {'staticPlot': True},
            #),
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
                id="town-graph",
                #config = {'staticPlot': True},
            ),
            #dcc.Graph(
            #    id="town-daily-graph",
            #    #config = {'staticPlot': True},
            #),
            #dcc.Graph(
            #    id="town-total-graph",
            #    #config = {'staticPlot': True},
            #),
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
            'title':'{} {}'.format(area, title),
            'barmode':'group',
            'bargroupgap':0.0,
            'xaxis':{'fixedrange':True,'tickformat':'%_m/%-d', 
                    },
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
            'title':'{} {}'.format(area, title),
            'xaxis':{'tickformat':'%_m/%-d', 
                     'fixedrange':True,
                    },
            'yaxis':{'fixedrange':True},
        }
    }

def create_ScatterIncRatioChart(dff, area, this_week_col, last_week_col, title, r_min_zero):
    # グラフの表示期間を限定する
    # 開始：inc_dec_start_date
    # 終了：最終更新日
    this_week_data = dff[this_week_col]
    last_week_data = dff[last_week_col]
    this_week_data_max = this_week_data.max()
    last_week_data_max = last_week_data.max()
    this_week_data_min = this_week_data.min()
    last_week_data_min = last_week_data.min()
    # グラフスケールの最大値を計算する
    if this_week_data_max > last_week_data_max:
        r_max = this_week_data_max
    else:
        r_max = last_week_data_max
    r_max = r_max*1.05
    # グラフスケールの最小値を計算する
    if this_week_data_min < last_week_data_min:
        r_min = this_week_data_min
    else:
        r_min = last_week_data_min
    r_min = r_min*0.95
    if r_min <= r_min_zero:
        r_min = 0
    # センターラインデータを作成する
    c_data = [0, r_max]
    # 増加・減少ラインデータを作成する
    x1_5_x_data = [0, r_max/1.5]
    x2_0_x_data = [0, r_max/2.0]
    x3_0_x_data = [0, r_max/3.0]
    x5_0_x_data = [0, r_max/5.0]
    x0_7_y_data = [0, r_max*(2.0/3.0)]
    x0_5_y_data = [0, r_max*(1.0/2.0)]
    target_line = dict(color = light_color, width = 3)
    center_line = dict(color = center_color, width = 3, dash='dot')
    inc_line = dict(color = inc_color, width = 2, dash='dot')
    dec_line = dict(color = dec_color, width = 2, dash='dot')
    last_update = dff.iloc[-1]['日付']
    #last_update = df_town_num_data.iloc[-1]['日付']
    if dff.iloc[-1]['先週累積'] == 0:
        last_week_ratio = np.nan
    else:
        last_week_ratio = dff.iloc[-1]['週累積']/dff.iloc[-1]['先週累積']
    annotations = [
        dict(text = 'x1.5',
             font = dict(color = inc_text_color),
             x = x1_5_x_data[-1],
             y = c_data[-1],
             xref = 'x',
             yref = 'y',
             ax = 0,
             ay = 5,
             xanchor = 'left', 
             yanchor = 'bottom',
             showarrow = False
        ),
        dict(text = 'x2.0',
             font = dict(color = inc_text_color),
             x = x2_0_x_data[-1],
             y = c_data[-1],
             xref = 'x',
             yref = 'y',
             ax = 0,
             ay = 5,
             xanchor = 'left', 
             yanchor = 'bottom',
             showarrow = False
        ),
        dict(text = 'x3.0',
             font = dict(color = inc_text_color),
             x = x3_0_x_data[-1],
             y = c_data[-1],
             xref = 'x',
             yref = 'y',
             ax = 0,
             ay = 5,
             xanchor = 'left', 
             yanchor = 'bottom',
             showarrow = False
        ),
        dict(text = 'x5.0',
             font = dict(color = inc_text_color),
             x = x5_0_x_data[-1],
             y = c_data[-1],
             xref = 'x',
             yref = 'y',
             ax = 0,
             ay = 5,
             xanchor = 'left', 
             yanchor = 'bottom',
             showarrow = False
        ),
        dict(text = 'x2/3',
             font = dict(color = dec_text_color),
             x = c_data[-1],
             y = x0_7_y_data[-1],
             xref = 'x',
             yref = 'y',
             ax = 5, 
             ay = 0, 
             xanchor = 'left', 
             showarrow = False
        ),
        dict(text = 'x1/2',
             font = dict(color = dec_text_color),
             x = c_data[-1],
             y = x0_5_y_data[-1],
             xref = 'x',
             yref = 'y',
             ax = 5, 
             ay = 0, 
             xanchor = 'left', 
             showarrow = False
        ),
        dict(text = 'x1.0',
             font = dict(color = center_text_color),
             x = c_data[-1],
             y = c_data[-1],
             xref = 'x',
             yref = 'y',
             ax = 5, 
             ay = 0, 
             xanchor = 'left', 
             showarrow = False
        ),
        dict(text = '{0}時点<br>前週増加比{1:.2f}'.format(last_update.strftime('%Y/%-m/%-d'),last_week_ratio),
             font = dict(size = 14),
             x = c_data[-1],
             y = c_data[-1]*0.05+r_min,
             #y = c_data[-1]*0.05,
             xref = 'x',
             yref = 'y',
             align = 'left',
             xanchor = 'right', 
             yanchor = 'bottom',
             showarrow = False
        ),
            ]

    return {
        'data': [go.Scatter(
                    x = c_data,
                    y = c_data,
                    mode = 'lines',
                    line = center_line,
                    name = 'x1.0'),
                 go.Scatter(
                    x = x1_5_x_data,
                    y = c_data,
                    mode = 'lines',
                    line = inc_line,
                    name = 'x1.5'),
                 go.Scatter(
                    x = x2_0_x_data,
                    y = c_data,
                    mode = 'lines',
                    line = inc_line,
                    name = 'x2.0'),
                 go.Scatter(
                    x = x3_0_x_data,
                    y = c_data,
                    mode = 'lines',
                    line = inc_line,
                    name = 'x3.0'),
                 go.Scatter(
                    x = x5_0_x_data,
                    y = c_data,
                    line = inc_line,
                    mode = 'lines',
                    name = 'x5.0'),
                 go.Scatter(
                    x = c_data,
                    y = x0_7_y_data,
                    line = dec_line,
                    mode = 'lines',
                    name = 'x2/3'),
                 go.Scatter(
                    x = c_data,
                    y = x0_5_y_data,
                    line = dec_line,
                    mode = 'lines',
                    name = 'x1/2'),
                 go.Scatter(
                    x = last_week_data,
                    y = this_week_data,
                    text = dff['日付'],
                    mode ='lines+markers+text',
                    texttemplate='%{text|%-m/%-d}',
                    textposition='bottom right',
                    name = '前週増加比',
                    line = target_line),
                ],
        'layout':{
            'margin':{'l':50, 'r':50, 't':100, 'b':30},
            #'margin':{'l':30, 'r':20, 't':100, 'b':30},
            'showlegend':False,
            'title':'{} {}'.format(area, title),
            'xaxis':{
                     #'fixedrange':True, 
                     'range':(r_min, r_max),
                     'title':{'text':'前週累計', 'font':{'size':12},'standoff':0},
                     #'constrain':'domain',
                     },
            'yaxis':{
                     #'fixedrange':True, 
                     'range':(r_min, r_max),
                     'title':{'text':'週累計', 'font':{'size':12},'standoff':0},
                     'scaleanchor':'x',
                     'scaleratio':1,
                     },
            'annotations':annotations
        }
    }

def rs_value2datetime(rs_value):
    return list(pd.to_datetime(rs_value, unit='s'))

@app.callback(
    dash.dependencies.Output('area-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-area', 'value'),
     dash.dependencies.Input('radio_inc_ratio_persons', 'value'),
     dash.dependencies.Input('radio_real_per_popu', 'value'),
     dash.dependencies.Input('slider_range_date', 'value'),
    ]
)
def update_graph(dropdown_value, radio_irp_value, radio_rpp_value, rs_value):
    dff = df_area_num_data[df_area_num_data['地域'] == dropdown_value]
    from_datetime, to_datetime = rs_value2datetime(rs_value)
    dff = dff[(dff['日付']>=from_datetime)&(dff['日付'] <=to_datetime)]
    if radio_irp_value == 'inc_ratio':
        if radio_rpp_value == 'real_persons': 
            return create_ScatterIncRatioChart(dff, dropdown_value, '週累積', '先週累積', '前週増加比', 35)
        else:
            return create_ScatterIncRatioChart(dff, dropdown_value, '週累積人口10万人当たり', '先週累積人口10万人当たり', '前週増加比', 1.4)
    else:
        if radio_rpp_value == 'real_persons':
            return create_BarScatterChart(dff, dropdown_value, '日別', '日別', '週平均', '7日平均', '陽性者')
        else:
            return create_BarScatterChart(dff, dropdown_value, '日別人口10万人当たり', '日別', '週平均人口10万人当たり', '7日平均', '陽性者')

@app.callback(
    dash.dependencies.Output('town-graph', 'figure'),
    [dash.dependencies.Input('dropdown-for-town', 'value'),
     dash.dependencies.Input('radio_inc_ratio_persons', 'value'),
     dash.dependencies.Input('radio_real_per_popu', 'value'),
     dash.dependencies.Input('slider_range_date', 'value'),
    ]
)
def update_graph(dropdown_value, radio_irp_value, radio_rpp_value, rs_value):
    dff = df_town_num_data[df_town_num_data['市町村'] == dropdown_value]
    from_datetime, to_datetime = rs_value2datetime(rs_value)
    dff = dff[(dff['日付']>=from_datetime)&(dff['日付'] <=to_datetime)]
    if radio_irp_value == 'inc_ratio':
        if radio_rpp_value == 'real_persons': 
            return create_ScatterIncRatioChart(dff, dropdown_value, '週累積', '先週累積', '前週増加比', 35)
        else:
            return create_ScatterIncRatioChart(dff, dropdown_value, '週累積人口10万人当たり', '先週累積人口10万人当たり', '前週増加比', 1.4)
    else:
        if radio_rpp_value == 'real_persons':
            return create_BarScatterChart(dff, dropdown_value, '日別', '日別', '週平均', '7日平均', '陽性者')
        else:
            return create_BarScatterChart(dff, dropdown_value, '日別人口10万人当たり', '日別', '週平均人口10万人当たり', '7日平均', '陽性者')

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

@app.callback(
    dash.dependencies.Output('slider-container', 'children'),
    [dash.dependencies.Input('slider_range_date', 'value')])
def update_output(rs_value):
    #if rs_value:
    from_datetime, to_datetime = rs_value2datetime(rs_value)
    return '{} 〜 {}'.format(from_datetime.strftime('%Y/%m/%d'), to_datetime.strftime('%Y/%m/%d'))

if __name__ == '__main__':
    app.run_server(debug=True)
#    app.run_server(debug=True, host='0.0.0.0', port=80)
