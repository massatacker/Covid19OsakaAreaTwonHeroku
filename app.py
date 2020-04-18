# -*- coding: utf-8 -*-
import dash  
import dash_core_components as dcc   
import dash_html_components as html
import plotly.graph_objs as go  
import pandas as pd 
import json 

import os

#input_filename = 'num_data.xlsx'
input_filename = 'Covid19_Osaka_NumData.xlsx'

df_num_data = pd.read_excel(input_filename)
#df = pd.read_csv('longform.csv', index_col=0)
#dfhokkaido = df[df['area']=='北海道']

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    html.Div(
        html.H1('大阪府の市区町村別新型コロナウィルス感染者数',
        style = {'textAlign': 'center'})
    ),
    html.Div(
        html.H1(id='add-hover-data',
        # 付け足し③
        style={'textAlign': 'center',
        'color': 'limegreen'})
    ),
    #dcc.RadioItems(
    dcc.Dropdown(
        id = 'dropdown-for-covid_osaka',
        options = [{'label': i, 'value': i} for i in df_num_data['居住地'].unique()],
        searchable=False,
        value = '大阪府大阪市'
    ),
    dcc.Graph(
        id="covid_osakaGraph",
    )
])

@app.callback(
    dash.dependencies.Output('covid_osakaGraph', 'figure'),
    [dash.dependencies.Input('dropdown-for-covid_osaka', 'value')]
)
def update_graph(factor):
    dff = df_num_data[df_num_data['居住地'] == factor]

    return {
        #'data': [go.Scatter(
    	'data': [go.Bar(
    		x = dff['日付'],
    		y = dff['人数']
    	)]
    }


@app.callback(
    dash.dependencies.Output('add-hover-data', 'children'),
    [dash.dependencies.Input('covid_osakaGraph', 'hoverData')]
)
def return_hoverdata(hoverData):
    # 付けたし④
    try:
        showData = '{}: {}人'.format(hoverData['points'][0]['x'], hoverData['points'][0]['y'])
        return showData
    except:
        pass

if __name__ == '__main__':
    app.run_server(debug=True)
#    app.run_server(debug=True, host='0.0.0.0', port=80)
