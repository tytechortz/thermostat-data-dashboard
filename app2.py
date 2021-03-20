import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_table as dash_table
from dash_table import Format
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import json
from datetime import datetime, timedelta
import datetime as dt
import math
import time
import requests
import csv
import numpy as np

import pandas as pd

offt = []
ont = []
current_temps_list = []
run_time = 86400

url = "http://10.0.1.7:8080"
urlin = "http://10.0.1.6:5000"

start = '2021-03-01 00:00:00.00000'
today = dt.datetime.now().strftime("%Y-%m-%d")
today_day = dt.datetime.now().strftime("%-m-%-d")
# print(today_day)

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
                    dash_table.DataTable(id='temp-datatable-interactivity',
                    style_data_conditional=[
                        # {
                        # 'if': {'column_id': 'Date',
                        # 'filter_query': '{{Date}} = {}'.format(df['Date']) },
                        # 'backgroundColor': 'dodgerblue'
                        # }
                    ]),
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
    html.Div(id='today-temp-data', style={'display':'none'}),
    html.Div(id='ont', style={'display':'none'}),
])

@app.callback(
    Output('max-run-time', 'children'),
    Input('on-time', 'children'))
def update_max_left_timer(on_time):
    ont = on_time

    t = dt.datetime.now()


    sec_left = 86400 - ((t.hour * 3600) + (t.minute * 60) + t.second)
    poss_sec_left = sec_left + ont
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
    Input('off-time', 'children'))
def update_run_timer(off_time):
    ot = int(off_time)
    # print(ot)


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
    Input('on-time', 'children'))
def update_run_timer(on_time):
    rt = on_time
    print(rt)

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
    Input('current-interval-component', 'n_intervals'))
def update_total_timer(n):

    t = dt.datetime.now()

    hours = 24 - t.hour - 1
    minutes = 60 - t.minute
    seconds = 60 - t.second

    # print(seconds)

    return daq.LEDDisplay(
    label='Time Left',
    value='{:02d}:{:02d}'.format(hours, minutes),
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
    daily_avg = daily_avg.loc[start:]
    today_avg = daily_avg.iloc[-1]
    daily_avg = daily_avg.to_frame()
    daily_avg = daily_avg.reset_index()

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

    now = dt.datetime.now().strftime("%H:%M")

    return daq.LEDDisplay(
    label='Time',
    value=now,
    color='orange'
    )

@app.callback(
    [Output('on-time', 'children'),
    Output('off-time', 'children')],
    [Input('current-interval-component', 'n_intervals'),
    Input('today-temp-data', 'children')])
def on_off(n, data):
    t = datetime.now()
    # print(t.day)
    df = pd.read_json(data)
    # print(df)

    time_val = df.unstack()
    # print(time_val)

    if df.empty == False:
        current_run_time = time_val['time_delta'].iloc[-1]
        current_run_time = int(current_run_time / 1000)
    else:
        current_run_time = 0

    # on_time = int(time_val['time_delta'].iloc[-1] / 1000)
    on_time = current_run_time
    # print(on_time)

    today_tot_seconds = (t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    off_time = today_tot_seconds - on_time

    return on_time, off_time

@app.callback([
    Output('change', 'children'),
    Output('current-temp', 'children'),
    Output('today-temp-data', 'children')],
    Input('current-interval-component', 'n_intervals'))
def current_temp(n):

    t = datetime.now()

    df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], parse_dates=['Time'], dtype={'Temp':'Float32'})
    df.set_index(df['Time'], inplace = True)
    df['Date'] = pd.to_datetime(df['Time'].dt.date)
    today = datetime.today();
    # print(today)
    today_date = datetime(today.year, today.month, today.day)

    df = df[(df['Date'] == today_date)]
    # print(df_today)
    f = df['Temp'][-1]
    # print(df)
    df['change'] = df['Temp'] - df['Temp'].shift(1)
    change = df['change'].iloc[-1]

    df['tvalue'] = df.index
    df['time_delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
    df['run'] = np.where(df['change'] > .2, 'true', (np.where(df['Temp'] > 118, 'true', 'false' )))

    dfrt = df[['Time','time_delta','run', 'tvalue']]

    dfrt.columns = ['Date', 'time_delta', 'run', 'tvalue']
    # print(dfrt)
    df_run = dfrt.loc[dfrt['run'] == 'true']

    df_run = df_run.groupby(pd.to_datetime(df_run['Date']).dt.strftime('%m-%d'))['time_delta'].sum().reset_index()

    df_run['Date'] = df_run['Date'].apply(lambda x: '2021-' + x)

    df_run['Date'] = pd.to_datetime(df_run['Date'])
    df_run = df_run.set_index('Date')
    # print(df_run)
    today_tot_seconds = int((t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
    today_tot_seconds = dt.timedelta(seconds=today_tot_seconds)
    #
    full_day_seconds = dt.timedelta(seconds=86400)
    #
    current_temp = f
    # print(df_run)

    return change, current_temp, df_run.to_json()

@app.callback(
    Output('temp-datatable-interactivity', 'data'),
    Output('temp-datatable-interactivity', 'columns'),
    [Input('outside-interval-component', 'children'),
    Input('daily-avg', 'children')])
def display_annual_table(n, daily_avg):
    print(n)
    df = pd.read_csv('./export_df.csv')

    data_types = df.dtypes
    # print(data_types)
    df['time_delta'] = df['time_delta'].str[7:15]
    # print(df)
    df = df.set_index(pd.DatetimeIndex(df['Date']))
    df['Date'] = df.index

    # df['Date'] = pd.to_datetime(df['Date'])
    # now = pd.Timestamp.now()
    # td = pd.to_timedelta('24:00:00')
    today = pd.to_datetime(datetime.now().date())
    # today = time.strftime("%Y-%m-%d")
    print(today)
    t = datetime.today()
    now = datetime.now()
    # print(t)
    tts = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    # tts = dt.total_seconds()
    # print(tts)
    tts = int(tts)
    # print(tts)

    df['time_delta'] = pd.to_timedelta(df['time_delta'])
    df['Run'] = df['time_delta'].apply(lambda x: x.total_seconds())
    df['Run'] = df['Run'].astype(int)
    # print(df)
    df['Off'] = np.where(df.index >= today, (tts - df['Run']), (86400 - df['Run']))
    print(df)

    # df['time_delta'] = df['time_delta'].apply(lambda x:strftime('%Y:%m:%d')
    # print(df)
    # df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], parse_dates=['Time'], dtype={'Temp':'Float32'})
    # df.set_index(df['Time'], inplace = True)
    # df['Date'] = pd.to_datetime(df['Time'].dt.date)
    #
    # df['change'] = df['Temp'] - df['Temp'].shift(1)
    # change = df['change'].iloc[-1]
    # df['tvalue'] = df.index
    # df['time_delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
    # df['run'] = np.where(df['change'] > .2, 'true', (np.where(df['Temp'] > 118, 'true', 'false' )))
    # dfrt = df[['Time','time_delta','run', 'tvalue']]
    #
    # dfrt.columns = ['Date', 'time_delta', 'run', 'tvalue']
    # # print(dfrt)
    # df_run = dfrt.loc[dfrt['run'] == 'true']
    #
    # df_run = df_run.groupby(pd.to_datetime(df_run['Date']).dt.strftime('%m-%d'))['time_delta'].sum().reset_index()
    #
    # df_run['Date'] = df_run['Date'].apply(lambda x: '2021-' + x)
    #
    # df_run['Date'] = pd.to_datetime(df_run['Date'])
    # df_run = df_run.set_index('Date')
    #
    #
    # print(type(df['time_delta'].loc[20]))
    #
    d_avg = pd.read_json(daily_avg)
    #
    d_avg['Time'] = d_avg['Time'].apply(lambda x: x / 1000)

    d_avg['Time'] = pd.to_datetime(d_avg['Time'], unit='s')

    d_avg = d_avg.set_index('Time')
    d_avg['Temp'] = d_avg['Temp'].round(1)
    #
    t = datetime.today()
    #
    # td = t.day
    #
    # df['seconds'] = df['time_delta'] / 1000
    #
    # today_run_seconds = df['time_delta'].iloc[-1] / 1000
    #
    # df = df.drop('time_delta', 1)
    # t = pd.Timestamp.now()
    # print(t)
    # #
    # tts = (t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    # tts = pd.to_timedelta(tts)
    # print(tts)
    #
    # pct_on = today_tot_seconds / today_run_seconds
    #
    # df['Pct Off'] = df['seconds'].apply(lambda x: (86400 - x) / 86400)
    # df['Pct Off'] = df['Pct Off'].astype(float).map("{:.2%}".format)
    # df['Run Time'] = df['seconds'].apply(lambda x: dt.timedelta(seconds=x))
    # df['Run Time'] = df['Run Time'].astype(str).str[6:15]
    # now = pd.Timestamp.now()
    # td = pd.to_timedelta('24:00:00')
    # print(type(td))

    #
    # df['Off Time'] = df['time_delta'].apply(lambda x: td - x)
    # df['Off_s'] = df['Off Time'] / np.timedelta64(1, 's')
    #
    # # print(df.columns)
    # df['Off_s'] = df['Off_s'].astype(int)
    #
    # df['Off Time'] = np.where(df.index.day == td, (tts - df['time_delta']), (td - df['time_delta']))
    # # print(df)
    # df['Off Time'] = df['Off Time'].apply(lambda x: dt.timedelta(seconds=x))
    #
    # df['Off Time'] = df['Off Time'].astype(str).str[6:15]
    df.rename(columns = {'time_delta':'On Time'}, inplace=True)
    df['On Time'] = df['On Time'].astype(str).str[6:15]
    df['Date'] = df['Date'].astype(str).str[6:15]

    #
    # df = pd.merge(df, d_avg, how = 'inner', left_index=True, right_index=True)
    df = df.sort_values(by=['On Time'], ascending = True)
    # df['Date'] = df.index.date
    # # print(df)
    df = df[['Date', 'On Time', 'Off']]
    #
    # df['Date'] = df['Date'].apply(lambda x: x.strftime('%m-%d'))


    columns=[
        {"name": i, "id": i, "selectable": True} for i in df.columns
    ]

    return df.to_dict('records'), columns

    # @app.callback(
    #     Output('daily-run-totals', 'children'),
    #     [Input('outside-interval-component', 'n_intervals'),
    #     Input('all-temp-data', 'children')])
    # def current_temp(n, data):
    #     df = pd.read_json(data)

        # t = datetime.now()
        #
        # df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], parse_dates=['Time'], dtype={'Temp':'Float32'})
        # df.set_index(df['Time'], inplace = True)
        # df['Date'] = pd.to_datetime(df['Time'].dt.date)
        # print(df)
        # today = datetime.today();
        # print(today)
        # today_date = datetime(today.year, today.month, today.day)
        # # print(df)
        # df_today = df_today[(df_today['Date'] == today_date)]
        #
        # f = df_today['Temp'][-1]
        #
        # df_today['change'] = df_today['Temp'] - df_today['Temp'].shift(1)
        # change = df_today['change'].iloc[-1]
        # df_today['tvalue'] = df_today.index
        # df_today['time_delta'] = (df_today['tvalue'] - df_today['tvalue'].shift()).fillna(0)
        # df_today['run'] = np.where(df_today['change'] > .2, 'true', (np.where(df_today['Temp'] > 118, 'true', 'false' )))
        # # print(df_today)
        # dfrt = df_today[['Time','time_delta','run', 'tvalue']]
        # # print(dfrt)
        # # df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], parse_dates=['Time'], dtype={'Temp':'Float32'})
        # #
        # # df.set_index(df['Time'], inplace = True)
        # # df['Date'] = pd.to_datetime(df['Time'].dt.date)
        #
        # # f = df['Temp'][-1]
        # #
        # # df['change'] = df['Temp'] - df['Temp'].shift(1)
        # # change = df['change'].iloc[-1]
        # # df['tvalue'] = df.index
        # # df['time_delta'] = (df['tvalue'] - df['tvalue'].shift()).fillna(0)
        # # df['run'] = np.where(df['change'] > .2, 'true', (np.where(df['Temp'] > 118, 'true', 'false' )))
        # #
        # # dfrt = df[['Time','time_delta','run', 'tvalue']]
        # dfrt.columns = ['Date', 'time_delta', 'run', 'tvalue']
        # # print(dfrt)
        # df_new = dfrt.loc[dfrt['run'] == 'true']
        #
        # df_new = df_new.groupby(pd.to_datetime(df_new['Date']).dt.strftime('%m-%d'))['time_delta'].sum().reset_index()
        #
        # df_new['Date'] = df_new['Date'].apply(lambda x: '2021-' + x)
        #
        # df_new['Date'] = pd.to_datetime(df_new['Date'])
        # df_new = df_new.set_index('Date')
        # # print(df_new)
        # today_tot_seconds = int((t - t.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        # today_tot_seconds = dt.timedelta(seconds=today_tot_seconds)
        #
        # full_day_seconds = dt.timedelta(seconds=86400)



        # return df_new.to_json()





if __name__ == '__main__':
    app.run_server(port=8050,debug=True)
