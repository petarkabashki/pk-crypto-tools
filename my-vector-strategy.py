# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#%%
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from collections import OrderedDict

from datetime import datetime
# import talib
import pandas_ta as ta
# from talib.abstract import *
from math import *
import seaborn as sns
#import vectorbt as vbt
import ffn

#%%

matplotlib.rcParams.update({'font.size': 5, 'lines.linewidth': 0.5, 'figure.dpi': 300})

#%%
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

#%%
start_time = datetime(2021,4,10)
end_time = datetime(2021,7,3)

ddf = df.loc[(df.index >= start_time) & (df.index <= end_time)].copy().sort_index()
# ddf = df.loc[df['time'] >= start_time]
# ddf
dlen = len(ddf.index)


ddf = ddf.resample('15Min').agg(
    OrderedDict([
        ('open', 'first'),
        ('high', 'max'),
        ('low', 'min'),
        ('close', 'last'),
        ('volume', 'sum'),
    ])
).dropna()

#%%


ddf['lret'] = ddf.close.apply(np.log).diff(1)
ddf['cumlret'] = ddf.lret.cumsum()

# bb_middleband = talib.EMA(ddf['close'], timeperiod=21)
ddf_bbands = ddf.ta.bbands(length=14, std=2.7, mamode='EMA', ddof=0, offset=None)

ddf_bbands.columns = ['bb_lower', 'bb_middle', 'bb_upper', 'bb_bandwidth', 'bb_percent']

# ddf = pd.concat([ddf, ddf_bbands])
ddf['mema'] = ta.ema(ddf.close, length=26)
# bb_upperband, bb_middleband, bb_lowerband = talib.BBANDS(ddf['close'], timeperiod=21, nbdevup=2., nbdevdn=2.5, matype=0)
# # len(bb_upperband), len(ddf)
# ddf['bb_upper'] = bb_upperband
# ddf['bb_middle'] = bb_middleband
# ddf['bb_lower'] = bb_lowerband


# krnl = np.linspace(0, 0.2, 10) ** 2 / 2 - 0.01
# krnl = krnl * 100



#%%

capital = 10000
pos_size = 100.
risk_per_trade = 0.01
take_profit = 0.03
fee = 0.001

#ddf['ema26'] = talib.EMA(ddf.close, 26)

# w1 = 50 # short-term moving average window
# w2 = 120 # long-term moving average window
# w3 = 240
# ma_x = ddf.close.rolling(w1).mean() - ddf.close.rolling(w2).mean()

# ddf['fema'] = talib.EMA(ddf.close, w1)
# ddf['sema'] = talib.EMA(ddf.close, w2)
# ddf['lema'] = talib.EMA(ddf.close, w3)
# tper = int(60 * 3)

# ddf['ret'] = ddf.close - ddf.close.shift(fill_value=0)
# ddf['pct_change'] = ddf.close.pct_change()
# ddf['sret'] = ddf.close / ddf.close.shift(fill_value=ddf.close[0])
# ddf['lret'] =   np.diff(np.log(ddf.close))
# ddf['lret'] = np.log(ddf.close.astype('float32')/ddf.close.astype('float32').shift(1))

# ddf['fufema'] = ddf.fema.shift(-tper)
# ddf['fumin'] = ddf.close.rolling(tper).min().shift(-tper)
# ddf['fumax'] = ddf.close.rolling(tper).max().shift(-tper)
# ddf['fuminperc'] = (ddf.fumin - ddf.close) / ddf.close * 100
# ddf['fumaxperc'] = (ddf.fumax - ddf.close) / ddf.close * 100
# ddf['fufemaperc'] = (ddf.fufema - ddf.close) / ddf.close * 100
# ddf['rr'] = ddf['fumaxperc'] / ddf['fuminperc']

# ddf['macd'] = ddf.fema - ddf.sema
# ddf['macdperc'] = np.log(ddf.macd / ddf.sema)

# bb_upper, bb_middle, bb_lower = talib.BBANDS(
#                                 ddf.close.values, 
#                                 timeperiod=w1,
#                                 # number of non-biased standard deviations from the mean
#                                 nbdevup=1.7,
#                                 nbdevdn=1.7,
#                                 # Moving average type: simple moving average here
#                                 matype=0)

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

def fill_sell_signals(ser):
    sell = ( (ser.posret < -0.01) | (ser.posret > 0.03) ).shift(fill_value=False)
    sell.iloc[-1] = True
    # idx = mask.idxmax() if mask.any() else np.repeat(False, len(df))
    sig_sell = pd.Series(False, index=ser.index)
    sig_sell.loc[sell.idxmax()] = True
    return sig_sell

ddf['sell'] = ddf[ddf.g_buy>0].groupby(g_buy).apply(fill_sell_signals).droplevel(0)
ddf['sell'].fillna(False, inplace=True)

# ddf[ddf.sell | ddf.buy][['buy','sell']]
# buys = ddf[ddf.buy].buy
# sells = ddf[ddf.sell].sell
# dummy_buys = (buys & sells.shift(fill_value=False))


trades = np.where(ddf.sell, pos_size * (ddf.posret - 2*fee), 0) #* (1 - 2*fee)
trades[0] = capital

equity = trades.cumsum()
ddf['equity'] = pd.Series(equity, index=ddf.index)
ddf['returns'] = ddf.equity.to_log_returns().dropna()

#

perf = ddf.equity.calc_stats()
perf.plot()

perf.display()

#
#%%
q = '"2021-06-01 00" <= time < "2021-06-29"'
wdf = ddf.query(q)
wdf_bbands = ddf_bbands.query(q)
# wta = ta.query(q)
# wdf_buys = wdf[wdf.buy > 0]
# wdf_sells = wdf[wdf.sell > 0]
# set downtrend values to 0
# wdf.loc[macd_lt0_mask, ['cross_cumlret', 'max_ret', 'min_ret', 'cross_since', 'trend_len']] = 0

#%%

plt.close("all")
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,1]},)
# fig.legend(fontsize=3)

ax1.plot(wdf.close)
ax1.plot(wdf.low, lw=0.3)
ax1.plot(wdf.high, lw=0.3)
ax1.plot(wdf_bbands.bb_lower)
ax1.plot(wdf_bbands.bb_upper)
ax1.plot(wdf_bbands.bb_middle)
ax1.plot(wdf.mema, lw=1)
# ax1.plot(wdf.fema)
# ax1.plot(wdf.sema)
# ax1.plot(wdf.lema)
ax1.fill_between(wdf_bbands.index, y1=wdf_bbands.bb_middle*0.99, y2=wdf_bbands.bb_middle*1.01, alpha=0.2 )
# ax1.vlines(wdf_buys.index, wdf.close.min(), wdf.close.max())
# ax1.vlines(wdf_sells.index, wdf.close.min(), wdf.close.max(),color='orange')

ax2.plot(wdf_bbands.bb_bandwidth)
ax2.plot(wdf_bbands.bb_percent)


ax3.plot(wdf.krnl_trend)

#%%
# ax2.plot(wdf.cumlret)
# ax2.plot(wdf.close)
# ax2.plot(wta.MA20)
# ax2.axhline(lw=0.5)
# ax2.vlines(wdf_buys.index, wdf.posret.min(), wdf.posret.max(),lw=0.2)
# ax2.vlines(wdf_sells.index, wdf.posret.min(), wdf.posret.max(),lw=0.2,color='orange')

# ax3.plot(g_buy[wdf.index], lw=0.2)
# ax3.vlines(wdf_buys.index, g_buy[wdf.index].min(), g_buy[wdf.index].max(),lw=0.2)
# ax3.vlines(wdf_sells.index, g_buy[wdf.index].min(), g_buy[wdf.index].max(),lw=0.2,color='orange')

# ax3.plot(wdf.equity)
# ax3.vlines(wdf_buys.index, wdf.equity.min(), wdf.equity.max(),lw=0.2)
# ax3.vlines(wdf_sells.index, wdf.equity.min(), wdf.equity.max(),lw=0.2,color='orange')

# ax4.plot(wdf.returns)
# plt.tick_params(labelsize=2)


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

#%% kernels

# idxs = np.arange(10)
krnl_len = 20
krnl_idxs = np.linspace(1/4 * pi, (2 - 1/4) * pi, krnl_len) 
# krnl = np.exp(np.sin(krnl_idxs) ) -2
# ** 2 #/ 2 - 0.01
# krnlx = np.array(krnlx * 100)
krnlx = np.flipud(krnl)

plt.close("all")
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios':[1,1]})
ax1.plot(krnl_idxs)
ax2.plot(krnl)
ax2.plot(krnlx)

#%%

ddf['krnl_trend'] = ddf.cumlret.rolling(16).apply(lambda v: (v * krnl).sum())

#%%

q = '"2021-06-2 00" <= time < "2021-06-7"'
wdf = ddf.query(q)
wdf_bbands = ddf_bbands.query(q)
wdf['sin_krn'] = wdf_bbands.bb_middle.rolling(krnl_len).apply(lambda v: (v * krnlx).sum())

wdf['sin_krn_gt0'] = wdf['sin_krn'] > 0
wdf_crosses = (wdf.sin_krn_gt0) & (~wdf.sin_krn_gt0).shift()

plt.close("all")
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,1]})

ax1.plot(wdf.close)
# ax1.plot(wdf.mema)
ax1.plot(wdf_bbands.bb_lower)
ax1.plot(wdf_bbands.bb_middle)

ax1.vlines(wdf_crosses[wdf_crosses].index, wdf.close.min(), wdf.close.max(),lw=0.5)
ax1.fill_between(wdf_bbands.index, y1=wdf_bbands.bb_middle*0.99, y2=wdf_bbands.bb_middle*1.01, alpha=0.1 )

# ax2.plot(wdf.cumlret.rolling(krnl_len).apply(lambda v: (v * krnl).sum()))
# ax2.plot(wdf.cumlret.rolling(krnl_len).apply(lambda v: (v * krnlx).sum()))
# ax2.axhline()
# ax3.plot(wdf_bbands.bb_middle.rolling(krnl_len).apply(lambda v: (v * krnl).sum()))
ax2.plot(wdf.sin_krn)
ax2.vlines(wdf_crosses[wdf_crosses].index, wdf.sin_krn.min(), wdf.sin_krn.max(),lw=0.5)
# ax2.axhline()

#%%


# distribution of period of uptrend > 0
zdf = ddf[macd_gt0_mask].groupby(g_cross).cross_since.max()
sns.displot(zdf, binwidth=5)

#%%
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
