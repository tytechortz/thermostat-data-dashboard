import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_table as dt
from dash_table import Format
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import json
from datetime import datetime
import math
import time
import requests
import csv
import numpy as np

import pandas as pd

offt = []
ont = []
start_time = datetime.now().minute
current_temps_list = []
run_time = 86400

url = "http://10.0.1.7:8080"
urlin = "http://10.0.1.6:5000"

# c=1
# print(on)
pd.options.display.float_format = '{:,.2f}'.format

app = dash.Dash(__name__)

time_start = time.time()
seconds = 0
minutes = 0
hours = 0

app.layout = html.Div([
    html.Div(id='current-temp-led'),

    # dcc.Graph(id='live-graph'),


    html.Div([
    #     html.Div([
    #         html.Div([
    #             html.Div([
    #                 html.Div(id='time-on-led'),
    #             ],
    #                 className='three columns'
    #             ),
    #             html.Div([
    #                 html.Div(id='time-off-led'),
    #             ],
    #                 className='three columns'
    #             ),
    #             html.Div([
    #                 html.Div(id='max-run-time'),
    #             ],
    #                 className='three columns'
    #             ),
    #             html.Div([
    #                 html.Div(id='pct-off-time'),
    #             ],
    #                 className='three columns'
    #             ),
    #         ],
    #             className='twelve columns'
    #         ),
    #     ],
    #         className='row'
    #     ),
    # ]),
    # html.Div([
        # html.Div([
        #     html.Div([
        #         html.Div([
        #             html.Div(id='total-time'),
        #         ],
        #             className='three columns'
        #         ),
        #         html.Div([
        #             html.Div(id='total-time-left'),
        #         ],
        #             className='three columns'
        #         ),
        #         html.Div([
        #             html.Div(id='pct-off-time-clinched'),
        #         ],
        #             className='three columns'
        #         ),
        #     ],
        #         className='twelve columns'
        #     ),
        # ],
        #     className='row'
        # ),
        html.Div([
            html.Div([
                html.Div([
                    html.Div(id='outside-t'),
                ],
                    className='three columns'
                ),
                html.Div([
                    html.Div(id='avg-outside-t'),
                ],
                    className='three columns'
                ),
            ],
                className='twelve columns'
            ),
        ],
            className='row'
        ),
        # html.Div([
        #     html.Div([
        #     #     html.Div([
        #     #         dt.DataTable(id='temp-datatable-interactivity'),
        #     #     ],
        #     #         className='five columns'
        #     #     ),
        #     # ],
        #     #     className='twelve columns'
        #     # ),
        # ],
        #     className='row'
        # ),
    ]),

    html.Div([
        dcc.Interval(
            id='interval-component',
            interval=10000,
            n_intervals=0
        ),
        dcc.Interval(
            id='outside-interval-component',
            interval=60000,
            n_intervals=0
        ),
        dcc.Interval(
            id='current-interval-component',
            interval=1000,
            n_intervals=0
        ),
    ]),
    html.Div(id='all-temp-data', style={'display':'none'}),
    html.Div(id='change', style={'display':'none'}),
    # html.Div(id='start-time', style={'display':'none'}),
    html.Div(id='on-time', style={'display':'none'}),
    html.Div(id='off-time', style={'display':'none'}),
    # html.Div(id='max-left', style={'display':'none'}),
    html.Div(id='current-temp', style={'display':'none'}),
    html.Div(id='daily-run-totals', style={'display':'none'}),
    html.Div(id='ont', style={'display':'none'}),
])

@app.callback(
    Output('outside-t', 'children'),
    Input('outside-interval-component', 'n_intervals'))
def outside_temp(n):
    res = requests.get(url)
    data = res.json()
    f = ((9.0/5.0) * data) + 32

    return daq.LEDDisplay(
        label='Outside T',
        value='{:,.2f}'.format(f),
        color='red'
    ),



if __name__ == '__main__':
    app.run_server(port=8050,debug=True)
