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
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(id='temp-datatable-interactivity'),
                ],
                    className='five columns'
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
    html.Div(id='all-temp-data', style={'display':'none'}),
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
    Output('temp-datatable-interactivity', 'table'),
    Input('interval-component', 'n_intervals'))
def display_daily_table(n):


    return dt.DataTable(id='temp-datatable-interactivity',
    data=[{}],
    columns=[{}],
    fixed_rows={'headers': True, 'data': 0},
    style_cell_conditional=[
        {'if': {'column_id': 'Date'},
        'width':'100px'},
        {'if': {'column_id': 'Value'},
        'width':'100px'},
    ],
    style_data_conditional=[
        {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
        },
    ],
    style_header={
    'backgroundColor': 'rgb(230, 230, 230)',
    'fontWeight': 'bold'
    },

    sort_action="native",
    sort_mode="multi",
    column_selectable="single",
    selected_columns=[],
    selected_rows=[],

    page_current= 0,
    page_size= 10,
    )


@app.callback([
    Output('temp-datatable-interactivity', 'data'),
    Output('temp-datatable-interactivity', 'columns')],
    [Input('all-temp-data', 'children'),
    Input('on-time', 'children')])
def display_annual_table(all_temp_data, on_time):
    df = pd.read_json(all_temp_data)
    t = datetime.now()
    # print(df.tail())

    df['tvalue'] = df.index
    df['time delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
    df['run'] = np.where(df['change'] > .1, 'true', 'false')
    df['run_time'] = df[df['run'] == 'true']['time delta'].cumsum()
    df['change'] = df['change'].fillna(0)
    # print(df.tail())

    # print(t)
    today_tot_seconds = (t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    # run_time_sum = df['run_time'].max()
    # print(today_tot_seconds)
    # pd.set_option("display.max_rows", None)
    # print(type(df['run_time'].iloc[-1]))
    # print(df['run_time'].max())
    run_time_sum = df['run_time'].max()
    on_time = on_time
    # print(on_time)
    df_days = df.resample('D').max()
    # df_days =
    # print(df_days.tail())
    # print(type(df_days['run_time'].max()))
    # df_days['run_time'] = df['run_time'].astype(int)



    df_days = df_days.drop(['Temp', 'change', 'run_tot', 'tvalue', 'run', 'time delta'], axis=1)



    df_days['Day'] = df_days.index.strftime('%Y-%m-%d')
    # df_days['run time'] = df_days['run_tot'] * 10
    # df_days['run time'] = df_days['run_time'].astype(int)
    #
    # df_days['minutes'] = df_days['run time'] // 60
    #
    # df_days['seconds'] = df_days['run time'] % 60
    #
    # df_days['hours'] = df_days['minutes'] // 60
    #
    # df_days['minutes1'] = df_days['minutes'] % 60
    # print(df_days.tail())
    # print(df_days['run_time'].iloc[-1])
    # print(type(df_days['run_time'].iloc[-1]))
    # df_days['run_time'] = pd.to_datetime(df['run_time'], format="%H:%M:%S")
    # df_days.Day = pd.DatetimeIndex(df.Day).strftime("%Y-%m-%d")
    # df_days['Run Time'] = (pd.to_datetime(df_days['hours'].astype(str) + ':'+ df_days['minutes1'].astype(str), format='%H:%M').dt.time)

    # df_days = df_days.drop(['Temp', 'change', 'run_tot', 'run time', 'hours', 'minutes', 'seconds', 'minutes1', 'time delta'], axis=1)

    columns=[
        # dict(id='1', name='Day', format=)
        # {"name": "Day", "id": "1", "selectable": True},
        # {"name": 'Run Time', "id": "2", "selectable": True},
        {"name": i, "id": i, "selectable": True} for i in df_days.columns
    ]

    return df_days.to_dict('records'), columns


@app.callback(
    Output('total-time', 'children'),
    Input('current-interval-component', 'n_intervals'))
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

    hours = 24 - t.hour - 1
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

    sec_left = 86400 - ((t.hour * 3600) + (t.minute * 60) + t.second)
    # print(sec_left)
    poss_sec_left = sec_left + ont
    # print(poss_sec_left)
    max_minutes = poss_sec_left // 60
    max_seconds = poss_sec_left % 60
    max_hours = max_minutes // 60
    max_minutes = max_minutes % 60

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
    pct_off_clinched = ot / 86400 * 100

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
    Input('all-temp-data', 'children')])
def on_off(n, data):
    t = datetime.now()
    # print(t.day)
    today = pd.to_datetime('today').normalize()
    #
    # print(type(today))
    # print()
    # hours = 24 - t.hour - 1
    # minutes = 60 - t.minute - 1
    # seconds = 60 - t.second


    df = pd.read_json(data)
    print(df.tail())
    # print(type(df.index))
    df['tvalue'] = df.index
    df['time delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
    df['run'] = np.where(df['change'] > .1, 'true', 'false')
    # df = df.loc['2021-202-25' : '2021-202-25']
    # print(type(df['time delta'].iloc[-1]))
    df['run_time'] = df[df['run'] == 'true']['time delta'].cumsum()
    df['change'] = df['change'].fillna(0)
    df = df.loc[str(today):]

    # df = df.loc[str(today):str(today)]
    print(df.tail())
    # df = df.resample('D').sum()
    # print(df)
    run_time_sum = df['run_time'].max()
    print(run_time_sum)
    # print(type(run_time_sum))

    on_time = run_time_sum / np.timedelta64(1, 's')
    print(on_time)
#
    today_tot_seconds = (t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    # print(today_tot_seconds)
    off_time = today_tot_seconds - on_time
    # print(off_time)

    # t = datetime.now()
    # ts = start_time
    # # df = pd.read_json(temp_data)
    # f = change
    # if t.hour == 0 and t.minute == 0 and t.second == 0:
    #     ont.clear()
    #     offt.clear()
    # if f > 0.15:
    #     ont.append(1)
    # else:
    #     offt.append(1)

    # on_time = len(ont)
    # off_time = len(offt)

    # on_time = 10
    # off_time = 20
    # print(on_time)
    # print(off_time)

    return on_time, off_time

# @app.callback(
#     [Output('on-time', 'children'),
#     Output('off-time', 'children')],
#     [Input('interval-component', 'n_intervals'),
#     Input('change', 'children')])
# def on_off(n, change):
#     t = datetime.now()
#     ts = start_time
#     # df = pd.read_json(temp_data)
#     f = change
#     if t.hour == 0 and t.minute == 0 and t.second == 0:
#         ont.clear()
#         offt.clear()
#     if f > 0.15:
#         ont.append(1)
#     else:
#         offt.append(1)
#
#     on_time = len(ont)
#     off_time = len(offt)
#     # print(on_time)
#     # print(off_time)
#
#     return on_time, off_time

@app.callback(
    Output('time-on-led', 'children'),
    [Input('interval-component', 'n_intervals'),
    Input('on-time', 'children')])
def update_run_timer(n, on_time):
    rt = on_time
    print(rt)


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
    [Input('off-time', 'children'),
    Input('current-interval-component', 'n_intervals')])
def update_run_timer(off_time, n):
    ot = int(off_time)
    print(change)
    print(n)


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
    Output('all-temp-data', 'children')],
    Input('current-interval-component', 'n_intervals'))
def current_temp(n):
    df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], index_col=['Time'], parse_dates=['Time'])
    # print(df)
    # df['Datetime'] = pd.to_datetime(df['Time'])
    # df = df.set_index('Datetime')
    # print(df)

    f = df['Temp'][-1]
    current_temps_list.append(f)

    # print(current_temps_list)
    # current_temp = current_temps_list[2]
    # previous_temp = current_temps_list[1]
    # current_temps_list.pop(0)
    # df['tvalue'] = df.index
    # df['time delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
    # df['run'] = np.where(df['change'] > .1, 'true', 'false')
    # df = df.loc['2021-202-25' : '2021-202-25']
    # print(type(df['time delta'].iloc[-1]))



    df['change'] = df['Temp'] - df['Temp'].shift(1)
    # print(df.tail())
    change = df['change'].iloc[-1]
    df['tvalue'] = df.index
    df['time delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
    df['run'] = np.where(df['change'] > .1, 'true', 'false')
    df['run_tot'] = np.where(df['run'] == 'true', 1, 0)
    df['run_time'] = df[df['run'] == 'true']['time delta'].cumsum()
    # df['change'] = df['change'].fillna(0)
    # df['cum_sum'] = df['run_tot'].cumsum()
    # df['run_tot'] = df['run_tot'].astype('float64')
    # df['run_on'] =pd.to_datetime(df['cum_sum'].dt.strftime("%H:%M:%S"))
    # print(df.tail())
    # print(change)

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
    print(ct)
    # print(n)
    return daq.LEDDisplay(
        label='Current Temp',
        value='{:,.2f}'.format(ct),
        color='red'
    ),


if __name__ == '__main__':
    app.run_server(port=8050,debug=True)
