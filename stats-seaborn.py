# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
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
start_time = datetime(2021,6,1)
end_time = datetime(2021,6,8)

ddf = df.loc[(df.index >= start_time) & (df.index <= end_time)].copy()
# ddf = df.loc[df['time'] >= start_time]
# ddf
dlen = len(ddf.index)

#ddf['ema26'] = talib.EMA(ddf.close, 26)
ddf['fema'] = talib.EMA(ddf.close, 50)
ddf['sema'] = talib.EMA(ddf.close, 120)

tper = int(60 * 3)
ddf['ret'] = ddf.close - ddf.close.shift()
ddf['fufema'] = ddf.fema.shift(-tper)
ddf['fumin'] = ddf.close.rolling(tper).min().shift(-tper)
ddf['fumax'] = ddf.close.rolling(tper).max().shift(-tper)
ddf['fuminperc'] = (ddf.fumin - ddf.close) / ddf.close * 100
ddf['fumaxperc'] = (ddf.fumax - ddf.close) / ddf.close * 100
ddf['fufemaperc'] = (ddf.fufema - ddf.close) / ddf.close * 100
ddf['rr'] = ddf['fumaxperc'] / ddf['fuminperc']

ddf['macd'] = ddf.fema - ddf.sema
ddf['macdperc'] = ddf.macd / ddf.sema * 100

macd_gt0_mask = (ddf['macd'] > 0)
macd_lt0_mask = ~(macd_gt0_mask)

# ddf['macd_gt0'] = macd_gt0_mask
cross_up_mask = (
        (macd_gt0_mask & macd_lt0_mask.shift(1).astype(bool)) 
    )

cross_dn_mask = (
        (macd_lt0_mask & macd_gt0_mask.shift(1).astype(bool))
    )

g_cross_up = cross_up_mask.shift(fill_value=0).cumsum()
ddf['cross_up_len'] = ddf.groupby(g_cross_up).cumcount()
ddf['cross_up_cumret'] = ddf.ret.groupby(g_cross_up).cumsum()

bdf = ddf[(ddf['macd']>=0) & (ddf['cross_up_len'] < 200)]

wdf = ddf.iloc[1:24*60*2, :]
wdf_up_crosses = wdf[wdf['cross_up_len'] == 0]

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,1]})
ax1.plot(wdf.close, lw=0.5)
#ax1.plot(wdf.ema26, lw=0.5)
ax1.plot(wdf.fema, lw=0.5)
ax1.plot(wdf.sema, lw=0.5)
# ax1.plot(wdf.fumin, lw=0.5)
# ax1.plot(wdf.fumax, lw=0.5)
# ax1.plot(wdf.fufema, lw=1.5)
ax1.vlines(wdf_up_crosses.index, wdf.close.min(), wdf.close.max(),lw=0.5)

ax2.plot(wdf.trend_up_cumret, lw=0.5)
# ax2.plot(wdf.fuminperc, lw=0.5)
# ax2.plot(wdf.fumaxperc, lw=0.5)
#ax2.plot(wdf.macdperc, lw=0.5)
ax2.axhline(lw=0.5)
ax2.vlines(wdf_up_crosses.index, wdf.cross_up_cumret.min(), wdf.cross_up_cumret.max(),lw=0.5)

ax3.plot(wdf.trend_up_len, lw=0.5)
# ax3.plot(wdf.macd, lw=0.5)
#ax3.plot(wdf.fumaxperc, lw=0.5)
ax3.axhline(lw=0.5)
ax3.vlines(wdf_up_crosses.index, wdf.cross_up_len.min(), wdf.cross_up_len.max(),lw=0.5)

#fig.show()

sns.displot(bdf, x="fufemaperc", y="trend_len", cbar=True)
sns.displot(bdf, x="fumaxperc", y="trend_len", cbar=True)

sns.jointplot(data=bdf, x="fufemaperc", y="trend_len", hue="fuminperc", s=1)
# sns.jointplot(data=bdf, x="fumaxperc", y="trend_len", s=1)

sns.displot(bdf, x="fufemaperc", hue="fuminperc", stat="probability")
sns.displot(bdf, x="fufemaperc", hue="fuminperc", kind="kde")
