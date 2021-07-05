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
import ffn


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

start_time = datetime(2021,5,10)
end_time = datetime(2021,5,20)

ddf = df.loc[(df.index >= start_time) & (df.index <= end_time)].copy().sort_index()
# ddf = df.loc[df['time'] >= start_time]
# ddf
dlen = len(ddf.index)

# ddf['cap'] = 10000.
capital = 10000
pos_size = 100.
risk_per_trade = 0.01
take_profit = 0.03
fee = 0.001

#ddf['ema26'] = talib.EMA(ddf.close, 26)

w1 = 50 # short-term moving average window
w2 = 120 # long-term moving average window
# ma_x = ddf.close.rolling(w1).mean() - ddf.close.rolling(w2).mean()

ddf['fema'] = talib.EMA(ddf.close, w1)
ddf['sema'] = talib.EMA(ddf.close, w2)

tper = int(60 * 3)

# ddf['ret'] = ddf.close - ddf.close.shift(fill_value=0)
# ddf['pct_change'] = ddf.close.pct_change()
# ddf['sret'] = ddf.close / ddf.close.shift(fill_value=ddf.close[0])
# ddf['lret'] =   np.diff(np.log(ddf.close))
# ddf['lret'] = np.log(ddf.close.astype('float32')/ddf.close.astype('float32').shift(1))
ddf['lret'] = ddf.close.apply(np.log).diff(1)

# ddf['fufema'] = ddf.fema.shift(-tper)
# ddf['fumin'] = ddf.close.rolling(tper).min().shift(-tper)
# ddf['fumax'] = ddf.close.rolling(tper).max().shift(-tper)
# ddf['fuminperc'] = (ddf.fumin - ddf.close) / ddf.close * 100
# ddf['fumaxperc'] = (ddf.fumax - ddf.close) / ddf.close * 100
# ddf['fufemaperc'] = (ddf.fufema - ddf.close) / ddf.close * 100
# ddf['rr'] = ddf['fumaxperc'] / ddf['fuminperc']

ddf['macd'] = ddf.fema - ddf.sema
ddf['macdperc'] = np.log(ddf.macd / ddf.sema)

# ddf.iloc[100:500]['lret'].cumsum().plot()

macd_gt0_mask = (ddf['macd'] > 0)
macd_lt0_mask = ~(macd_gt0_mask)
# ddf['macd_gt0_mask'] = macd_gt0_mask
# ddf['macd_lt0_mask'] = macd_lt0_mask

# ddf['macd_gt0'] = macd_gt0_mask
cross_up_mask = (
        (macd_gt0_mask & macd_lt0_mask.shift(fill_value=False).astype(bool)) 
    )

cross_dn_mask = (
        (macd_lt0_mask & macd_gt0_mask.shift(fill_value=False).astype(bool))
    )


buy_sig = cross_up_mask.shift(fill_value=False)
g_buy = buy_sig.cumsum()
# g_sell = cross_dn_mask.shift(fill_value=0).cumsum()


ddf['g_buy'] = g_buy
ddf['buy'] = buy_sig
ddf['posret'] = ddf.groupby(g_buy).lret.cumsum()
ddf['buy_since'] = ddf.groupby(g_buy).cumcount()

def fill_signals(ser):
    sell = ( (ser.posret < -0.01) | (ser.posret > 0.02) ).shift(fill_value=False)
    sell.iloc[-1] = True
    # idx = mask.idxmax() if mask.any() else np.repeat(False, len(df))
    sig_sell = pd.Series(False, index=ser.index)
    sig_sell.loc[sell.idxmax()] = True
    return sig_sell

ddf['sell'] = ddf[ddf.g_buy>0].groupby(g_buy).apply(fill_signals).droplevel(0)
ddf['sell'].fillna(False, inplace=True)

# ser = ddf[ddf.g_buy==14]
# sell = ( (ser.posret < -0.01) | (ser.posret > 0.02) ).shift(fill_value=False)
# sell.iloc[-1] = True
# sig_sell = pd.Series(False, index=ser.index)
# sig_sell.loc[sell.idxmax()] = True

sells = ddf[ddf.sell]
trades = np.where(ddf.sell, pos_size * (ddf.posret - 2*fee), 0) #* (1 - 2*fee)
trades[0] = capital

equity = trades.cumsum()
ddf['equity'] = pd.Series(equity, index=ddf.index)
# pnl = ddf[ddf.sell]


wdf = ddf.query('"2021-05-01 00" <= time < "2021-05-30 14"')

# wdf_buys = wdf[wdf['trade_rule'] == 1]
# wdf_sells = wdf[wdf['trade_rule'] == -1]
wdf_buys = wdf[wdf.buy > 0]
wdf_sells = wdf[wdf.sell > 0]
# set downtrend values to 0
# wdf.loc[macd_lt0_mask, ['cross_cumlret', 'max_ret', 'min_ret', 'cross_since', 'trend_len']] = 0

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,1,1]})
ax1.plot(wdf.close, lw=0.2)
#ax1.plot(wdf.ema26, lw=0.5)
ax1.plot(wdf.fema, lw=0.2)
ax1.plot(wdf.sema, lw=0.2)
ax1.fill_between(wdf.index, y1=wdf.fema*0.995, y2=wdf.fema*1.005, alpha=0.2 )
ax1.vlines(wdf_buys.index, wdf.close.min(), wdf.close.max(),lw=0.2)
ax1.vlines(wdf_sells.index, wdf.close.min(), wdf.close.max(),lw=0.2,color='orange')


ax2.plot(wdf.posret, lw=0.2)
ax2.axhline(lw=0.5)
# ax2.vlines(wdf_buys.index, wdf.posret.min(), wdf.posret.max(),lw=0.2)
# ax2.vlines(wdf_sells.index, wdf.posret.min(), wdf.posret.max(),lw=0.2,color='orange')

# ax3.plot(g_buy[wdf.index], lw=0.2)
# ax3.vlines(wdf_buys.index, g_buy[wdf.index].min(), g_buy[wdf.index].max(),lw=0.2)
# ax3.vlines(wdf_sells.index, g_buy[wdf.index].min(), g_buy[wdf.index].max(),lw=0.2,color='orange')

ax3.plot(wdf.equity, lw=0.5)
# ax3.vlines(wdf_buys.index, wdf.equity.min(), wdf.equity.max(),lw=0.2)
# ax3.vlines(wdf_sells.index, wdf.equity.min(), wdf.equity.max(),lw=0.2,color='orange')

# ax2.plot(wdf.cross_cumlret, lw=0.5)
# ax2.plot(wdf.max_ret, lw=0.5)
# ax2.plot(wdf.min_ret, lw=0.5)
# ax2.axhline(lw=0.5)
# ax2.vlines(wdf_crosses.index, wdf.cross_cumlret.min(), wdf.cross_cumlret.max(),lw=0.5)
# ax2.fill_between(wdf.index, wdf.cross_cumlret.min(), wdf.cross_cumlret.max(),alpha=0.9, 
#                  color='grey', where=wdf.macd_lt0_mask)

# ax3.plot(wdf.cross_since, lw=0.5)
# ax3.plot(wdf.trend_len, lw=0.5)
# ax3.axhline(lw=0.5)
# ax3.vlines(wdf_crosses.index, wdf.cross_since.min(), wdf.cross_since.max(),lw=0.5)
# ax3.fill_between(wdf.index, wdf.cross_since.min(), wdf.cross_since.max(),alpha=0.9, 
#                  color='grey', where=wdf.macd_lt0_mask)

# ax4.plot(wdf.g_cross)
# ax4.vlines(wdf_crosses.index, wdf.g_cross.min(), wdf.g_cross.max(),lw=0.5)
# ax4.fill_between(wdf.index, wdf.g_cross.min(), wdf.g_cross.max(),alpha=0.9, 
#                  color='grey', where=wdf.macd_lt0_mask)


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
