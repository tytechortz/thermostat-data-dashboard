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
import datetime
import math
import time
import requests
import csv
import numpy as np

import pandas as pd

offt = []
ont = []
# start_time = datetime.now().minute
current_temps_list = []
run_time = 86400

url = "http://10.0.1.7:8080"
urlin = "http://10.0.1.6:5000"

start = '2021-03-01'
today = datetime.datetime.now().strftime("%Y-%m-%d")
print(today)

# c=1
# print(on)
pd.options.display.float_format = '{:,.2f}'.format

app = dash.Dash(__name__)

time_start = time.time()
seconds = 0
minutes = 0
hours = 0

app.layout = html.Div([

    # dcc.Graph(id='live-graph'),

    html.Div([
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
                html.Div([
                    html.Div(id='current-temp-led'),
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
                    html.Div(html.P('-', id='placeholder')),
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
    html.Div(id='daily-avg', style={'display':'none'}),
    html.Div(id='current-temp', style={'display':'none'}),
    html.Div(id='daily-run-totals', style={'display':'none'}),
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
    style_cell={'textAlign': 'left22', 'backgroundColor': 'rgb(30, 30, 30)'},
    style_cell_conditional=[
        {'if': {'column_id': 'Date'},
        'width':'100px'},
        {'if': {'column_id': 'Value'},
        'width':'100px'},
    ],
    style_data_conditional=[
        {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(30, 30, 30)'
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
    [Input('daily-run-totals', 'children'),
    Input('daily-avg', 'children')])
def display_annual_table(temp_data, daily_avg):
    df = pd.read_json(temp_data)

    daily_avg = pd.read_csv(daily_avg)
    # print(daily_avg)

    t = datetime.datetime.now()

    # print(type(df.index))
    df.reset_index(inplace=True)

    df['Month'], df['Day'] = df['index'].str[1:2], df['index'].str[3:4]
    df = df.drop('index', 1)
    df['seconds'] = df['time_delta'] / 1000
    today_run_seconds = df['time_delta'].iloc[-1] / 1000
    df = df.drop('time_delta', 1)

    today_tot_seconds = (t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    pct_on = today_tot_seconds / today_run_seconds
    # print(pct_on)


    # print(today_run_seconds)

    # print(df)
    # pd.options.display.float_format = '{:,.2f}'.format

    df['Pct Off'] = df['seconds'].apply(lambda x: (86400 - x) / 86400)
    df['Pct Off'] = df['Pct Off'].astype(float).map("{:.2%}".format)
    df['Run Time'] = df['seconds'].apply(lambda x: datetime.timedelta(seconds=x))
    df['Run Time'] = df['Run Time'].apply(lambda x: str(x))
    df['Date'] = df['Month'] +'-'+df['Day']
    df = df.drop(['Month', 'Day', 'seconds'], axis=1)
    df = df[['Date', 'Pct Off', 'Run Time']]



    # print(today_tot_seconds)

    columns=[
        {"name": i, "id": i, "selectable": True} for i in df.columns
    ]

    return df.to_dict('records'), columns

@app.callback(
    Output('max-run-time', 'children'),
    Input('on-time', 'children'))
def update_max_left_timer(on_time):
    ont = on_time
    # print(ont)
    t = datetime.datetime.now()
    # print(t.minute)

    sec_left = 86400 - ((t.hour * 3600) + (t.minute * 60) + t.second)
    # print(sec_left)
    poss_sec_left = sec_left + ont
    # print(poss_sec_left)
    max_minutes = poss_sec_left // 60
    max_seconds = poss_sec_left % 60
    max_hours = max_minutes // 60
    max_minutes = max_minutes % 60


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

    rt = run_count
    ot = off_count

    pct_off = ot / (rt + ot) * 100

    return daq.LEDDisplay(
    label='Pct Off',
    value='{:.2f}'.format(pct_off),
    color='blue'
    ),

@app.callback(
    Output('time-off-led', 'children'),
    [Input('off-time', 'children'),
    Input('current-interval-component', 'n_intervals')])
def update_run_timer(off_time, n):
    ot = int(off_time)


    minutes = ot // 60
    seconds = ot % 60
    hours = minutes //60
    minutes = minutes % 60


    return daq.LEDDisplay(
    label='Off Time',
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='blue'
    ),

@app.callback(
    Output('time-on-led', 'children'),
    [Input('interval-component', 'n_intervals'),
    Input('on-time', 'children')])
def update_run_timer(n, on_time):
    rt = on_time

    minutes = rt // 60
    seconds = rt % 60
    hours = minutes //60
    minutes = minutes % 60

    return daq.LEDDisplay(
    label='Run Time',
    # value=rt,
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='red'
    ),

@app.callback(
    Output('total-time-left', 'children'),
    Input('on-time', 'children'))
def update_total_timer(on_time):
    ot = on_time
    t = datetime.datetime.now()

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
    [Output('avg-outside-t', 'children'),
    Output('daily-avg', 'children')],
    Input('outside-interval-component', 'n_intervals'))
def avg_outside_temp(n):
    df = pd.read_csv('../../tempjan19.csv', names=['Time', 'Temp'], index_col=['Time'], parse_dates=['Time'])

    daily_avg = df['Temp'].resample('D').mean()
    daily_avg = df.loc[start:today]
    print(daily_avg)
    today_avg = daily_avg.iloc[-1]

    return daq.LEDDisplay(
        label='Outside  Avg T',
        value='{:,.2f}'.format(today_avg),
        color='red'
    ), daily_avg.to_json()

@app.callback(
    Output('current-temp-led', 'children'),
    [Input('current-temp', 'children'),
    Input('current-interval-component', 'n_intervals')])
def update_ct_led(current_temp, n):
    ct = current_temp
    # print(ct)
    return daq.LEDDisplay(
        label='Current Temp',
        value='{:,.2f}'.format(ct),
        color='red'
    ),

@app.callback(
    Output('total-time', 'children'),
    Input('current-interval-component', 'n_intervals'))
def update_total_timer(n):

    now = datetime.datetime.now().strftime("%H:%M:%S")

    return daq.LEDDisplay(
    label='Time',
    value=now,
    color='orange'
    )

@app.callback(
    [Output('on-time', 'children'),
    Output('off-time', 'children')],
    [Input('current-interval-component', 'n_intervals'),
    Input('daily-run-totals', 'children')])
def on_off(n, data):
    t = datetime.datetime.now()
    df = pd.read_json(data)

    time_val = df.unstack()
    # print(time_val.columns)

    current_run_time = time_val['time_delta'].iloc[-1]
    current_run_time = int(current_run_time / 1000)

    on_time = current_run_time

    today_tot_seconds = (t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    off_time = today_tot_seconds - current_run_time

    return on_time, off_time

@app.callback([
    Output('change', 'children'),
    Output('current-temp', 'children'),
    Output('all-temp-data', 'children'),
    Output('daily-run-totals', 'children')],
    Input('current-interval-component', 'n_intervals'))
def current_temp(n):
    df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], parse_dates=['Time'])
    # print(df.tail())
    df.set_index(df['Time'], inplace = True)
    df['Date'] = pd.to_datetime(df['Time'].dt.date)

    f = df['Temp'][-1]

    df['change'] = df['Temp'] - df['Temp'].shift(1)
    # print(df.tail())
    change = df['change'].iloc[-1]
    df['tvalue'] = df.index
    df['time_delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
    # print(df.tail())
    df['run'] = np.where(df['change'] > .2, 'true', (np.where(df['Temp'] > 118, 'true', 'false' )))

    dfrt = df[['Time','time_delta','run']]
    dfrt.columns = ['Date', 'time_delta', 'run']

    df_new = dfrt.loc[dfrt['run'] == 'true']
    df_hell = df_new.groupby([df_new['Date'].dt.month, df_new['Date'].dt.day]).agg({'time_delta':sum})

    current_temp = f

    return change, current_temp, df.to_json(), df_hell.to_json()



if __name__ == '__main__':
    app.run_server(port=8050,debug=True)
