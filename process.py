import pandas as pd
from datetime import datetime
import schedule
import time
import numpy as np
# import datetime

def table_data():
    df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], parse_dates=['Time'], dtype={'Temp':'Float32'})
    df.set_index(df['Time'], inplace = True)
    df['Date'] = pd.to_datetime(df['Time'].dt.date)

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
    df_run.to_csv('export_df.csv', header=True)

    print(df_run)

schedule.every().minute.do(table_data)

while 1:
    schedule.run_pending()
    time.sleep(1)
