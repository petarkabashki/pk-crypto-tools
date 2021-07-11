#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 00:09:09 2021

@author: johnsmith
"""


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from datetime import datetime
import talib
import pandas_ta as ta
from talib.abstract import *
from math import *
import pandas_ta as ta
import seaborn as sns
#import vectorbt as vbt

df = pd.read_json(r'freq-user-data/data/binance/BTC_USDT-1m.json')
df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

df['time'] = pd.to_datetime(df['timestamp'], unit='ms', utc=False)
# df.index = df['time']
# df.set_index('time', drop=True, inplace=True)
df.set_index(pd.DatetimeIndex(df["time"]), inplace=True, drop=True)
# df = df[['time', 'symbol', 'source', 'resolution', 'open', 'high', 'low', 'close', 'volume']]
# df.to_csv (r'./data/binance/BTC_USDT-5m.csv', index = None)
# df.set_index('time')

# pd.Timestamp('now').floor('D') + pd.Timedelta(-7, unit='D')

# start_time = pd.Timestamp('now').floor('D') + pd.Timedelta(-7, unit='D')

# start_time = pd.Timestamp('now') + pd.Timedelta(-2, unit='W')

start_time = datetime(2021,5,1)
end_time = datetime(2021,6,30)

ddf = df.loc[(df.index >= start_time) & (df.index <= end_time)].copy()
# ddf = df.loc[df['time'] >= start_time]
# ddf
dlen = len(ddf.index)


prices = ddf.close
rs = prices.apply(np.log).diff(1)
# rs.plot()

w1 = 50 # short-term moving average window
w2 = 120 # long-term moving average window
ma_x = prices.rolling(w1).mean() - prices.rolling(w2).mean()

pos = ma_x.apply(np.sign) # +1 if long, -1 if short

fig, ax = plt.subplots(2,1)
ma_x.plot(ax=ax[0], title='Moving Average Cross-Over', lw=0.5)
pos.plot(ax=ax[1], title='Position', lw=0.5)

my_rs = pos.shift(1)*rs

my_rs.cumsum().apply(np.exp).plot(title='Strategy Performance', lw=0.5)

# with lags

lags = range(5, 11)
lagged_rs = pd.Series(dtype=float, index=lags)
for lag in lags:
    my_rs = (pos.shift(lag)*rs) #.sum()
    np.exp(my_rs.cumsum()).plot(lw=0.5)
    lagged_rs[lag] = my_rs.sum()
plt.title('Strategy Performance with Lags') 
plt.legend(lags, bbox_to_anchor=(1.1, 0.95))

#\

tc_pct = 0.001 # assume transaction cost of 1% 
delta_pos = pos.diff(1).abs() #.sum(1) # compute portfolio changes
my_tcs = tc_pct*delta_pos # compute transaction costs
my_rs1 = (pos.shift(1)*rs) #.sum(1) # don't include costs
my_rs2 = (pos.shift(1)*rs) - my_tcs #.sum(1) - my_tcs # include costs
my_rs1.cumsum().apply(np.exp).plot(lw=0.5)
my_rs2.cumsum().apply(np.exp).plot(lw=0.5)
plt.legend(['without transaction costs', 'with transaction costs'])
