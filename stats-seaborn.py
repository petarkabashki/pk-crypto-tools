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

start_time = datetime(2021,5,1)
end_time = datetime(2021,7,1)

ddf = df.loc[(df.index >= start_time) & (df.index <= end_time)].copy()
# ddf = df.loc[df['time'] >= start_time]
# ddf
dlen = len(ddf.index)

#ddf['ema26'] = talib.EMA(ddf.close, 26)
ddf['fema'] = talib.EMA(ddf.close, 50)
ddf['sema'] = talib.EMA(ddf.close, 120)

tper = int(60 * 3)

# ddf['ret'] = ddf.close - ddf.close.shift(fill_value=0)
# ddf['pct_change'] = ddf.close.pct_change()
# ddf['sret'] = ddf.close / ddf.close.shift(fill_value=ddf.close[0])
# ddf['lret'] =   np.diff(np.log(ddf.close))
ddf['lret'] = np.log(ddf.close.astype('float32')/ddf.close.astype('float32').shift(1))
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
ddf['macd_gt0_mask'] = macd_gt0_mask
ddf['macd_lt0_mask'] = macd_lt0_mask

# ddf['macd_gt0'] = macd_gt0_mask
cross_up_mask = (
        (macd_gt0_mask & macd_lt0_mask.shift(1).astype(bool)) 
    )

cross_dn_mask = (
        (macd_lt0_mask & macd_gt0_mask.shift(1).astype(bool))
    )

cross_mask = cross_up_mask | cross_dn_mask
g_cross = cross_mask.shift(fill_value=0).cumsum()
ddf['g_cross'] = g_cross
ddf['cross_since'] = ddf.groupby(g_cross).cumcount()
ddf['cross_cumlret'] = ddf.lret.groupby(g_cross).cumsum()

ddf['trend_len'] = ddf.groupby(['macd_gt0_mask','g_cross']).cross_since.transform('max')
ddf['max_ret'] = ddf.groupby(['macd_gt0_mask','g_cross']).cross_cumlret.transform('max')
ddf['min_ret'] = ddf.groupby(['macd_gt0_mask','g_cross']).cross_cumlret.transform('min')

# g_cross_up = cross_up_mask.shift(fill_value=0).cumsum()
# ddf['g_cross_up'] = g_cross_up
# ddf['cross_up_len'] = ddf.groupby(g_cross_up).cumcount()
# # ddf['cross_up_cumret'] = ddf.ret.groupby(g_cross_up).cumsum()
# ddf['cross_up_cumlret'] = ddf.groupby(g_cross_up).lret.cumsum()
# ddf['cross_up_cum_percret'] = np.exp(ddf['cross_up_cumlret']) - 1

# bdf = ddf[(ddf['macd']>=0) & (ddf['cross_up_len'] < 200)]

wdf = ddf.iloc[1:24*60*2, :].copy()
wdf_crosses = wdf[wdf['cross_since'] == 0]
# set downtrend values to 0
# wdf.loc[macd_lt0_mask, ['cross_cumlret', 'max_ret', 'min_ret', 'cross_since', 'trend_len']] = 0

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,1,1]})
ax1.plot(wdf.close, lw=0.5)
#ax1.plot(wdf.ema26, lw=0.5)
ax1.plot(wdf.fema, lw=0.5)
ax1.plot(wdf.sema, lw=0.5)
ax1.fill_between(wdf.index, y1=wdf.fema*0.995, y2=wdf.fema*1.005, alpha=0.2 )
ax1.vlines(wdf_crosses.index, wdf.close.min(), wdf.close.max(),lw=0.5)

ax2.plot(wdf.cross_cumlret, lw=0.5)
ax2.plot(wdf.max_ret, lw=0.5)
ax2.plot(wdf.min_ret, lw=0.5)
ax2.axhline(lw=0.5)
ax2.vlines(wdf_crosses.index, wdf.cross_cumlret.min(), wdf.cross_cumlret.max(),lw=0.5)
ax2.fill_between(wdf.index, wdf.cross_cumlret.min(), wdf.cross_cumlret.max(),alpha=0.9, 
                 color='grey', where=wdf.macd_lt0_mask)

ax3.plot(wdf.cross_since, lw=0.5)
ax3.plot(wdf.trend_len, lw=0.5)
ax3.axhline(lw=0.5)
ax3.vlines(wdf_crosses.index, wdf.cross_since.min(), wdf.cross_since.max(),lw=0.5)
ax3.fill_between(wdf.index, wdf.cross_since.min(), wdf.cross_since.max(),alpha=0.9, 
                 color='grey', where=wdf.macd_lt0_mask)

ax4.plot(wdf.g_cross)
ax4.vlines(wdf_crosses.index, wdf.g_cross.min(), wdf.g_cross.max(),lw=0.5)
ax4.fill_between(wdf.index, wdf.g_cross.min(), wdf.g_cross.max(),alpha=0.9, 
                 color='grey', where=wdf.macd_lt0_mask)


# 


# distribution of period of uptrend > 0
zdf = ddf[macd_gt0_mask].groupby(g_cross).cross_since.max()
sns.displot(zdf, binwidth=5)


# distribution of max cumulative log returns when macd > 0
# zdf = ddf[macd_gt0_mask].groupby(g_cross).cross_cumlret.max()
sns.displot(ddf[macd_gt0_mask].max_ret)

# distribution of min cumulative log returns when macd > 0
zdf = ddf[macd_gt0_mask].groupby(g_cross).cross_cumlret.min()
sns.displot(zdf)


zdf = ddf[macd_gt0_mask].groupby(g_cross).first()

sns.displot(zdf, x="trend_len", y="max_ret", hue='min_ret', cbar=False)

sns.displot(bdf, x="fumaxperc", y="trend_len", cbar=True)

sns.jointplot(data=bdf, x="fufemaperc", y="trend_len", hue="fuminperc", s=1)
# sns.jointplot(data=bdf, x="fumaxperc", y="trend_len", s=1)

sns.displot(bdf, x="fufemaperc", hue="fuminperc", stat="probability")
sns.displot(bdf, x="fufemaperc", hue="fuminperc", kind="kde")
