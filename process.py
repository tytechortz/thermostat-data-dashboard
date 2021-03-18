import pandas as pd
from datetime import datetime
# import datetime

df = pd.read_csv('../../thermotemps.txt', names=['Time', 'Temp'], parse_dates=['Time'], dtype={'Temp':'Float32'})
df.set_index(df['Time'], inplace = True)
df['Date'] = pd.to_datetime(df['Time'].dt.date)
today = datetime.today();
print(today)
today_date = datetime(today.year, today.month, today.day)
# print(df)
df = df[(df['Date'] == today_date)]
# print(df)
# today = datetime.today();
# print(today)
# today_date = datetime(today.year, today.month, today.day)
#
print(df)
