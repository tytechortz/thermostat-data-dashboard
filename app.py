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
import math
import time
import requests
import csv

import pandas as pd
on_time = []
off_time= []
on = []
run_time = 86400




# starttime = time.time()
# while True:
#     print('tick')
#     time.sleep(60.0 - ((time.time() - starttime) % 60.0))

url = "http://10.0.1.7:8080"

# c=1
# print(on)
pd.options.display.float_format = '{:,.2f}'.format

app = dash.Dash(__name__)


# def start_time():
#     time_start = time.time()
#     return time_start
# # time_start = time.time()
seconds = 0
minutes = 0
hours = 0


app.layout = html.Div([
    html.Div(id='current-temp-led'),

    dcc.Graph(id='live-graph'),


    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div(id='run-time-led'),
                ],
                    className='three columns'
                ),
                html.Div([
                    html.Div(id='time-off'),
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
                # html.Div([
                #     html.Div(
                #         html.Button('Start', id='start-button', n_clicks=0),
                #     )
                # ],
                #     className='one column'
                # ),
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
                        html.Div([
                            dt.DataTable(id='temp-datatable-interactivity'),
                        ]),
                    ],
                        className='four columns'
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
            interval=1000,
            n_intervals=0
        ),
        dcc.Interval(
            id='outside-interval-component',
            interval=60000,
            n_intervals=0
        ),
    ]),
    html.Div(id='temp-data', style={'display':'none'}),
    html.Div(id='change', style={'display':'none'}),
    html.Div(id='start-time', style={'display':'none'}),
    html.Div(id='on-time', style={'display':'none'}),
    html.Div(id='off-time', style={'display':'none'}),
    html.Div(id='max-left', style={'display':'none'}),
    html.Div(id='dummy', style={'display':'none'}),
    # html.Div(id='daily-run-time', style={'display':'none'}),
])

# @app.callback(
#     Output('daily-run-time', 'children'),
#     Input('on-time', 'children'))
#     # Input('outside-interval-component', 'n_intervals')])
# def get_daily_run_time(run_time):
#     rt = run_time
#     print(rt)
#     rt = str(rt)
#
#     with open('time', 'a') as f:
#         f.write(rt)
#         # writer = csv.writer(f)
#         # writer.writerow(rt)
#     return rt
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
    [Input('temp-data', 'children'),
    Input('on-time', 'children')])
def display_annual_table(temp_data, on_time):
    df = pd.read_json(temp_data)
    # print(df.tail())
    on_time = on_time
    print(on_time)
    df = df.drop('Change', axis=1)


        # annual_min_all = powell_dr.loc[powell_dr.groupby(pd.Grouper(freq='Y')).idxmin().iloc[:, 0]]
        #
        # annual_min_all = annual_min_all.iloc[37:]
        #
        # dr = annual_min_all
        #
        # dr = dr.sort_values('Value')
        #
        # dr = dr.drop(['Site', 'power level'], 1)
        #
        # dr = dr.reset_index()
        # dr = dr.rename(columns={dr.columns[0]: "Date"})
        # dr['Date'] = dr['Date'].dt.strftime('%Y-%m-%d')
        #
        # dr['Diff'] = dr['Value'] - dr['Value'].shift(1)

    columns=[
        {"name": i, "id": i, "selectable": True} for i in df.columns
    ]

    return df.to_dict('records'), columns

@app.callback(
    Output('start-time', 'children'),
    Input('dummy', 'children'))
def time_output(dummy):

    start_time = time.time()
        # print(type(start_time))
    return start_time

# @app.callback(
#
# )
# def save_run_time()

@app.callback(
    Output('run-time-led', 'children'),
    [Input('interval-component', 'n_intervals'),
    Input('on-time', 'children')])
def update_run_timer(n, run_count):

    rt = run_count
    # print(rt)
    # print(rt)
    # with open(r'time', 'a') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(rt)

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
    Output('pct-off-time', 'children'),
    [Input('on-time', 'children'),
    Input('off-time', 'children')])
def pct_off_timer(run_count, off_count):

    rt = int(run_count)
    ot = int(off_count)
    # print(rt)
    # print(ot)

    pct_off = ot / (rt + ot) * 100
    # print(pct_off)


    return daq.LEDDisplay(
    label='Pct Off',
    value='{:.2f}'.format(pct_off),
    color='blue'
    ),

@app.callback(
    Output('time-off', 'children'),
    Input('off-time', 'children'))
def update_run_timer(time_off):
    rt = time_off
    # print(rt)

    minutes = rt // 60
    seconds = rt % 60
    hours = minutes //60
    minutes = minutes % 60

    return daq.LEDDisplay(
    label='Off Time',
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='blue'
    ),

@app.callback(
    Output('max-run-time', 'children'),
    Input('max-left', 'children'))
def update_max_left_timer(max_left):
    rt = max_left
    # print(rt)

    minutes = rt // 60
    seconds = rt % 60
    hours = minutes //60
    minutes = minutes % 60

    return daq.LEDDisplay(
    label='Max Time',
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='black'
    ),


@app.callback(
    [Output('on-time', 'children'),
    Output('off-time', 'children'),
    Output('max-left', 'children')],
    [Input('interval-component', 'n_intervals'),
    # Input('start-time', 'children'),
    # Input('start-button', 'n_clicks'),
    Input('temp-data', 'children')])
def on_off(n,temp_data):
    df = pd.read_json(temp_data)

    if df['Change'].iloc[-1] > 0.1 or df['Temp'].iloc[-1] >= 119:
        on_time.append(1)
    elif df['Change'].iloc[-1] <=0.1:
        off_time.append(1)

    ont=len(on_time)
    offt=len(off_time)
    max_left= run_time - offt
    # print(max_left)

    return ont, offt, max_left


@app.callback(
    Output('total-time', 'children'),
    [Input('off-time', 'children'),
    Input('on-time', 'children')])
def update_total_timer(off_time, on_time):
    # start_time = start_time
    # print(start_time)

    # elapsed_time = off_time + on_time
    # print(elapsed_time)

    # minutes = elapsed_time // 60
    # seconds = elapsed_time % 60
    # hours = minutes //60
    # minutes = minutes % 60
    # print(n)
    now = datetime.now().strftime("%H:%M:%S")
    print(now)
    return daq.LEDDisplay(
    label='Time',
    # value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    value=now,
    color='orange'
    )

@app.callback(
    Output('total-time-left', 'children'),
    [Input('interval-component', 'n_intervals'),
    # Input('start-time', 'children'),
    Input('off-time', 'children'),
    Input('on-time', 'children')])
def update_total_timer(n, off_time, on_time):

    # start_time = start_time

    elapsed_time = off_time + on_time
    time_left = run_time - elapsed_time

    minutes = time_left // 60
    seconds = time_left % 60
    hours = minutes //60
    minutes = minutes % 60
    # print(n)
    return daq.LEDDisplay(
    label='Time Left',
    value='{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds),
    color='orange'
    )


@app.callback(
    Output('current-temp-led', 'children'),
    Input('temp-data', 'children'))
def update_leds(temp_data):
    df = pd.read_json(temp_data)
    # print(temp_data)
    current_temp = df['Temp'].iloc[-1]
    # print(current_temp)
    return daq.LEDDisplay(
        # id='current-temp-LED',
        label='Current Temp',
        value=current_temp,
        color='red'
    ),

@app.callback(
    [Output('temp-data', 'children'),
    Output('change', 'children')],
    [Input('interval-component', 'n_intervals'),
    Input('start-time', 'children')])
def fetch_data(n, start_time):

    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

    # print(start_time)
    df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'])
    pd.to_datetime(df['Time'])
    df.set_index('Time')

    df['MA'] = df.rolling(window=3)['Temp'].mean()
    df['Change'] = df['MA'] - df['MA'].shift(1)
    # print(df.head())
    df = df[df['Time'] > start_time]

    current_temp = df['MA'].iloc[-1]
    previous_temp = df['MA'].iloc[-2]

    change = current_temp - previous_temp

    df['Temp'] = df['Temp'].round(2)
    # print(df)
    return df.to_json(), change


@app.callback(
    Output('avg-outside-t', 'children'),
    Input('outside-interval-component', 'n_intervals'))
def avg_outside_temp(n):
    df = pd.read_csv('../../tempjan19.csv', names=['Time', 'Temp'], index_col=['Time'], parse_dates=['Time'])

    daily_avg = df['Temp'].resample('D').mean()

    today_avg = daily_avg.iloc[-1]
    # print(today_avg)

    return daq.LEDDisplay(
        # id='current-temp-LED',
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
    df = pd.read_csv('../../tempjan19.csv', names=['Time', 'Temp'])
    current_temp = df['Temp'].iloc[-1]
    # print(current_temp)

    return daq.LEDDisplay(
        # id='current-temp-LED',
        label='Outside T',
        value='{:,.2f}'.format(f),
        color='red'
    ),


@app.callback(
    Output('live-graph', 'figure'),
    Input('temp-data', 'children'))
def update_graph(temp_data):
    df = pd.read_json(temp_data)
    # start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

    fig = px.line(df, x='Time', y='MA')

    return fig


if __name__ == '__main__':
    app.run_server(port=8080,debug=True)
