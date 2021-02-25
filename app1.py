import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_table as dt
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import json
from datetime import datetime
# from collections import counter
import math
import time
import requests
import csv
import numpy as np

import pandas as pd
# on_time = []
offt = []
ont = []
start_time = datetime.now().minute
# on = []
current_temps_list = []
run_time = 86400


# starttime = time.time()
# while True:
#     print('tick')
#     time.sleep(60.0 - ((time.time() - starttime) % 60.0))

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
        html.Div([
            html.Div([
                html.Div([
                    html.Div(id='time-on-led'),
                ],
                    className='three columns'
                ),
                html.Div([
                    html.Div(id='time-off-led'),
                ],
                    className='three columns'
                ),
                html.Div([
                    html.Div(id='max-run-time'),
                ],
                    className='three columns'
                ),
                html.Div([
                    html.Div(id='pct-off-time'),
                ],
                    className='three columns'
                ),
            ],
                className='twelve columns'
            ),
        ],
            className='row'
        ),
    ]),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div(id='total-time'),
                ],
                    className='three columns'
                ),
                html.Div([
                    html.Div(id='total-time-left'),
                ],
                    className='three columns'
                ),
                html.Div([
                    html.Div(id='pct-off-time-clinched'),
                ],
                    className='three columns'
                ),
            ],
                className='twelve columns'
            ),
        ],
            className='row'
        ),
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
    html.Div(id='temp-data', style={'display':'none'}),
    html.Div(id='change', style={'display':'none'}),
    # html.Div(id='start-time', style={'display':'none'}),
    html.Div(id='on-time', style={'display':'none'}),
    html.Div(id='off-time', style={'display':'none'}),
    # html.Div(id='max-left', style={'display':'none'}),
    html.Div(id='current-temp', style={'display':'none'}),
    # html.Div(id='previous-temp', style={'display':'none'}),
    # html.Div(id='daily-run-time', style={'display':'none'}),
    # html.Div(id='new-offt', style={'display':'none'}),
    html.Div(id='ont', style={'display':'none'}),
])

@app.callback(
    Output('total-time', 'children'),
    Input('interval-component', 'n_intervals'))
def update_total_timer(n):

    now = datetime.now().strftime("%H:%M:%S")

    return daq.LEDDisplay(
    label='Time',
    value=now,
    color='orange'
    )

@app.callback(
    Output('avg-outside-t', 'children'),
    Input('outside-interval-component', 'n_intervals'))
def avg_outside_temp(n):
    df = pd.read_csv('../../tempjan19.csv', names=['Time', 'Temp'], index_col=['Time'], parse_dates=['Time'])

    daily_avg = df['Temp'].resample('D').mean()

    today_avg = daily_avg.iloc[-1]

    return daq.LEDDisplay(
        label='Outside  Avg T',
        value='{:,.2f}'.format(today_avg),
        color='red'
    ),

@app.callback(
    Output('outside-t', 'children'),
    Input('outside-interval-component', 'n_intervals'))
def outside_temp(n):
    res = requests.get(url)
    data = res.json()
    f = ((9.0/5.0) * data) + 32
    # df = pd.read_csv('../../tempjan19.csv', names=['Time', 'Temp'])
    # current_temp = df['Temp'].iloc[-1]

    return daq.LEDDisplay(
        label='Outside T',
        value='{:,.2f}'.format(f),
        color='red'
    ),

@app.callback(
    Output('total-time-left', 'children'),
    Input('on-time', 'children'))
def update_total_timer(on_time):
    ot = on_time
    t = datetime.now()

    # hours = 1 - t.hour
    minutes = 60 - t.minute - 1
    seconds = 60 - t.second

    # print(seconds)

    return daq.LEDDisplay(
    label='Time Left',
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='orange'
    )

@app.callback(
    Output('max-run-time', 'children'),
    Input('on-time', 'children'))
def update_max_left_timer(on_time):
    ont = on_time
    print(ont)
    t = datetime.now()
    # print(t.minute)

    sec_left = 3600 - ((t.minute * 60) + t.second)
    print(sec_left)
    poss_sec_left = sec_left + ont
    print(poss_sec_left)
    max_minutes = poss_sec_left // 60
    max_seconds = poss_sec_left % 60
    max_minutes = max_minutes % 60
    max_hours = 0
    # poss_sec_left = sec_left + ot
    # print(poss_sec_left)

    # max_minutes = sec_left // 60
    # max_seconds = sec_left % 60
    # max_hours = max_minutes // 60
    # max_minutes = max_minutes % 60

    return daq.LEDDisplay(
    label='Max Time',
    value='{:02d}:{:02d}:{:02d}'.format(max_hours, max_minutes, max_seconds),
    color='black'
    )

@app.callback(
    Output('pct-off-time-clinched', 'children'),
    [Input('on-time', 'children'),
    Input('off-time', 'children')])
def pct_off_timer(run_count, off_count):

    rt = int(run_count)
    ot = int(off_count)

    pct_off = ot / (rt + ot) * 100
    pct_off_clinched = ot / 3600 * 100

    return daq.LEDDisplay(
    label=' Min Pct Off',
    value='{:.2f}'.format(pct_off_clinched),
    color='blue'
    ),

@app.callback(
    Output('pct-off-time', 'children'),
    [Input('on-time', 'children'),
    Input('off-time', 'children')])
def pct_off_timer(run_count, off_count):

    rt = int(run_count)
    ot = int(off_count)

    pct_off = ot / (rt + ot) * 100

    return daq.LEDDisplay(
    label='Pct Off',
    value='{:.2f}'.format(pct_off),
    color='blue'
    ),

@app.callback(
    [Output('on-time', 'children'),
    Output('off-time', 'children')],
    [Input('interval-component', 'n_intervals'),
    Input('change', 'children')])
def on_off(n, change):
    t = datetime.now()
    ts = start_time
    # df = pd.read_json(temp_data)
    f = change
    if t.minute == 0 and t.second == 0:
        ont.clear()
        offt.clear()
    if f > 0.1:
        ont.append(1)
    else:
        offt.append(1)

    on_time = len(ont)
    off_time = len(offt)
    # print(on_time)
    # print(off_time)

    return on_time, off_time

@app.callback(
    Output('time-on-led', 'children'),
    [Input('interval-component', 'n_intervals'),
    Input('on-time', 'children')])
def update_run_timer(n, on_time):
    rt = on_time
    # print(rt)


    # print(rt)
    minutes = rt // 60
    seconds = rt % 60
    hours = minutes //60
    minutes = minutes % 60

    return daq.LEDDisplay(
    label='Run Time',
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='red'
    ),

@app.callback(
    Output('time-off-led', 'children'),
    [Input('change', 'children'),
    Input('off-time', 'children')])
def update_run_timer(change, off_time):
    ot = off_time
    # print(off_time)

    # print(rt)
    minutes = ot // 60
    seconds = ot % 60
    hours = minutes // 60
    minutes = minutes % 60

    return daq.LEDDisplay(
    label='Off Time',
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='blue'
    ),


@app.callback([
    Output('change', 'children'),
    Output('current-temp', 'children'),
    Output('temp-data', 'children')],
    Input('current-interval-component', 'n_intervals'))
def current_temp(n):
    df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], index_col=['Time'], parse_dates=['Time'])
    # print(df
    f = df['Temp'][-1]
    current_temps_list.append(f)

    # print(current_temps_list)
    # current_temp = current_temps_list[2]
    # previous_temp = current_temps_list[1]
    # current_temps_list.pop(0)



    df['change'] = df['Temp'] - df['Temp'].shift(1)
    # print(df.tail())
    change = df['change'].iloc[-1]

    # ont = len(df[df['change'] > 0.1])
    # offt = len(df[df['change'] <= 0.1])
    # print(ont)
    # print(offt)



    current_temp = f
    # print(current_temp)

    current_temp = df['Temp'].iloc[-1]
    previous_temp = df['Temp'].iloc[-2]
    # print(current_temp)

    change = current_temp - previous_temp
    # print(change)

    # df['Temp'] = df['Temp'].round(2)

    return change, current_temp, df.to_json()

@app.callback(
    Output('current-temp-led', 'children'),
    Input('current-temp', 'children'))
def update_leds(current_temp):
    ct = current_temp
    # print(ct)
    # print(n)
    return daq.LEDDisplay(
        label='Current Temp',
        value='{:,.2f}'.format(ct),
        color='red'
    ),


if __name__ == '__main__':
    app.run_server(port=8050,debug=True)
