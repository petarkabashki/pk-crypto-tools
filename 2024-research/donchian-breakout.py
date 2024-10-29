#%%
# %load_ext autoreload
# %autoreload 2
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_ta as ta
import math
from tqdm import tqdm
import gc
import time
import json
import pandas_ta
import talib
from pprint import pprint
# from position_tools import calculate_trades, calculate_positions, count_since_last_signal
# from pklibs import *
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pklib.strategy import *
from pklib.utilities import *
import optuna
optuna.logging.set_verbosity(optuna.logging.ERROR)
# You can use Matplotlib instead of Plotly for visualization by simply replacing `optuna.visualization` with
# `optuna.visualization.matplotlib` in the following examples.
from optuna.visualization import plot_contour
from optuna.visualization import plot_edf
from optuna.visualization import plot_intermediate_values
from optuna.visualization import plot_optimization_history
from optuna.visualization import plot_parallel_coordinate
from optuna.visualization import plot_param_importances
from optuna.visualization import plot_rank
from optuna.visualization import plot_slice
from optuna.visualization import plot_timeline

param_defs = {
    # 'ema_short_period': {'method': 'suggest_int', 'min': 10, 'max': 200, 'step':5},
    # 'ema_long_period': {
    #     'method': 'suggest_int',
    #     'min': 100,
    #     'max': 300,
    #     'step': 10,
    #     'min_depends_on': {
    #         'param': 'ema_short_period',
    #         'adjust_min': lambda ema_short: ema_short + 1
    #     }
    # },
    # 'ewo_enter': {'method': 'suggest_float', 'min': -1, 'max': 1, 'step': 0.01},
    # 'ewo_exit': {'method': 'suggest_float', 'min': -1, 'max': 1},
    # 'ewo_thre_short': {'method': 'suggest_float', 'min': -1, 'max': -0.01},
    # 'ema_filter_period': {'method': 'suggest_int', 'min': 200, 'max': 600, 'step': 20},
    'up_lookback': {'method': 'suggest_int', 'min': 10, 'max': 100, 'step': 5, 'adjust_start': True},
    'dn_lookback': {'method': 'suggest_int', 'min': 10, 'max': 100, 'step': 5, 'adjust_start': True},
    'up_lag': {'method': 'suggest_int', 'min': 5, 'max': 100, 'step': 3, 'adjust_start': True},
    'dn_lag': {'method': 'suggest_int', 'min': 5, 'max': 100, 'step': 3, 'adjust_start': True},
    'band_offset': {'method': 'suggest_float', 'min': 0, 'max': 1.0, 'step':0.1},
    'atr_period': {'method': 'suggest_int', 'min': 3, 'max': 50, 'step': 3, 'adjust_start': True},
    # 'band_offset_up': {'method': 'suggest_float', 'min': 0, 'max': 1.0},
    # 'band_offset_dn': {'method': 'suggest_float', 'min': 0, 'max': 1.0},
}
#%%
def skip_first_fn(param_defs, params):
    return max(
        [value for key, value in params.items() if param_defs.get(key, {}).get('adjust_start', False)],
        default=0
    )
  
def calculate_indicators(ohlcv, params):    
    atr = talib.ATR(ohlcv['high'], ohlcv['low'], ohlcv['close'], timeperiod=params['atr_period'])
    data_norm = ohlcv[['open','high','low','close']].divide(atr, axis=0)
    
    donch_up = data_norm['close'].rolling(window=params['up_lookback']).max().shift(params['up_lag'])
    donch_dn = data_norm['close'].rolling(window=params['dn_lookback']).min().shift(params['dn_lag'])
    donch_mid = (1 - params['band_offset']) * donch_up + params['band_offset'] * donch_dn
    
    log_price = data['close'].apply(np.log)
    return {
        'ohlcv': ohlcv, 'atr': atr, 'donch_up': donch_up, 'donch_dn': donch_dn, 'donch_mid': donch_mid, 'log_price': log_price,
        'data_norm': data_norm
    }
    
def generate_long_enter_signal(indicators):
    bull = (indicators['data_norm']['close'] > indicators['donch_up'])
    return (
                bull & (~bull.shift(fill_value=False))
                & (indicators['donch_up'] > indicators['donch_dn'])
                # & (data['close'] > data['ema_filter'])
                # & (data['ewo'] > params['ewo_enter'])
            ).astype(int)#.shift(fill_value=0)
def generate_long_exit_signal(indicators):
    return (
            (indicators['data_norm']['close'] < indicators['donch_mid'])
            # | (data['close'] < data['ema_filter'])
            ).astype(int)#.shift(fill_value=0)
def generate_short_enter_signal(indicators):
    return (
                (indicators['data_norm']['close'] < indicators['donch_dn'])  #& (~data['donch_up'].isna()) & (~data['donch_dn'].isna())
                & (indicators['donch_up'] < indicators['donch_dn'])
            ).astype(int)
def generate_short_exit_signal(indicators):
    return (
            (indicators['data_norm']['close'] > indicators['donch_mid'])
            ).astype(int)
#%%
signals_generator = {
        'long_enter': generate_long_enter_signal,
        'long_exit': generate_long_exit_signal,
        'short_enter': generate_short_enter_signal,
        'short_exit': generate_short_exit_signal,
}


#%%

def backtest(log_price, enter_sigs, exit_sigs, skip_first, xmult, transaction_cost=0.001, slippage=0.003, precision=3, period_costs=None):
 
    # Use the position_tools C extension for trade calculation
    
    entry_indices, exit_indices = position_tools.enumerate_trades(enter_sigs.values, exit_sigs.values, skip_first)

    if len(entry_indices) == 0:
        # print('No trades found.')
        return [], [], {}

    # Calculate trade returns using log prices
    trade_rets = pd.Series(
        xmult * (log_price.iloc[exit_indices].values - log_price.iloc[entry_indices].values),
        index=log_price.index[exit_indices]
    )
    trade_rets -= np.log1p(2*transaction_cost + slippage)

    metrics = calculate_metrics(trade_rets)

    return entry_indices, exit_indices, metrics


def optimize_strategy(ohlcv, param_defs, indicators_fn, signals_generator, skip_first_fn, btargs, long_short, n_trials=100, optimize_metrics=None, directions=None):
    
    # Define default directions for each metric
    default_directions = {
        'sharpe_ratio': 'maximize',
        'sortino_ratio': 'maximize',
        'max_drawdown': 'maximize',
        'tot_return': 'maximize',
        'avg_drawdown': 'minimize',
        'avg_win': 'maximize',
        'avg_loss': 'minimize',
        'win_ratio': 'maximize',
        'profit_factor': 'maximize',
        'n_trades': 'minimize',  # Depending on the context, some may want to minimize this
        'max_win': 'maximize',
        'max_loss': 'minimize',
    }
    
    # long_short = 'long'
    xmult = [1,-1][long_short=='short']
    
    # Set default metrics if none provided
    if optimize_metrics is None:
        optimize_metrics = ['sharpe_ratio']  # Default metric
    
    # Apply default directions if none are provided
    if directions is None:
        directions = [default_directions.get(metric.split('.')[-1], 'maximize') for metric in optimize_metrics]
    
    # Check for mismatched lengths
    if len(optimize_metrics) != len(directions):
        raise ValueError("The number of optimize metrics must match the number of directions.")
    
    def objective(trial):
        params = suggest_params(trial, param_defs)
        indicators = indicators_fn(data, params)
        entry_indices, exit_indices, metrics = comp_backtest(indicators,param_defs,params, signals_generator, long_short=long_short, skip_first_fn=skip_first_fn, flip_signal=False, btargs=btargs)
        
        if not metrics:
            return [float('-inf') if d == 'maximize' else float('inf') for d in directions]
        
        results = []
        for metric, direction in zip(optimize_metrics, directions):
            value = None

            # Check if metric is a function
            if callable(metric):
                value = metric(metrics)
            else:
                value = get_nested_metric(metrics, metric)

            # Apply default value if metric not found
            if value is None or np.isnan(value):
                value = float('-inf') if direction == 'maximize' else float('inf')

            results.append(value)
        # print('results: ', results)
        return results

    # Set up the study with the correct directions for multiple objectives
    study = optuna.create_study(directions=directions)
    study.optimize(objective, n_trials=n_trials)
    return study


def comp_backtest(indicators,param_defs,params, signals_generator, long_short, skip_first_fn, flip_signal=False, btargs={}):
    
    # long_short = 'long'
    xmult = [1, -1][long_short == 'short']
    xmult = [xmult, -xmult][flip_signal]
    
    enter_sigs = signals_generator[f'{long_short}_enter'](indicators)
    exit_sigs = signals_generator[f'{long_short}_exit'](indicators)  # Fixed to correctly reference the exit signals
    
    skip_first = skip_first_fn(param_defs, params)
    
    if skip_first >= len(data):
        return None, None, None
    
    entry_indices, exit_indices, metrics = backtest(indicators['log_price'], enter_sigs, exit_sigs, skip_first, xmult, **btargs)
    return entry_indices, exit_indices, metrics


def plot_strategy(indicators,metrics,entry_indices,exit_indices,convert_to_pct=False, mult_100=False, title=''):
    if len(entry_indices) > 0:
        print_metrics_table(metrics, convert_to_pct=convert_to_pct, mult_100=mult_100)
        
        if len(entry_indices) == 0:
            print("No trades found.")
            return None
            
            
        cum_returns = metrics['cum_returns']

        data = indicators['data_norm']
        # Align the cumulative returns with the trade exit indices
        pnl_pct = pd.concat([
            pd.Series(cum_returns, index=data.index.values[exit_indices]),
            pd.Series(cum_returns.shift(fill_value=0).values, index=data.index.values[entry_indices])
        ]).sort_index().apply(np.expm1)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 7), sharex=True, height_ratios=[2,1])

        ax2.axhline(0, color='black', lw=1)  
        if len(pnl_pct) > 0:
            ax2.plot(pnl_pct.index, pnl_pct * 100, label='PNL %', color='green', alpha=0.8, lw=2)
        ax2.legend(loc='best')
        ax2.set_title('Strategy performance')

        # Plot entry and exit points
        for x in data.index[entry_indices]: 
            ax1.axvline(x, color='blue', lw=1, alpha=0.2)
            ax2.axvline(x, color='blue', lw=1, alpha=0.2)
        for xx in data.index[exit_indices]:
            ax1.axvline(xx, color='green', lw=1, alpha=0.2)
            ax2.axvline(xx, color='green', lw=1, alpha=0.2)
        for i in range(len(entry_indices)):
            # color = ['red', 'green'][list((metrics['returns'].values < 0).astype(int))]
            # color = [['green','red'][i] for i in (metrics['returns'] < 0.0).values.astype(int)]
            color = 'gray'
            ax1.axvspan(xmin=data.index[entry_indices[i]], xmax=data.index[exit_indices[i]], color=color, alpha=0.1)
            ax2.axvspan(xmin=data.index[entry_indices[i]], xmax=data.index[exit_indices[i]], color=color, alpha=0.1)
        
        ax2.grid(axis='y')
        # plt.show()

        # fig = plot_performance(entry_indices, exit_indices, metrics,data)
        fig.suptitle(title)
        donc_up = indicators['donch_up']
        donc_dn = indicators['donch_dn']
        donch_mid = indicators['donch_mid']
        # if not fig_train is None:
        # plot_indicators(fig.get_axes()[0], data,price_only=price_only)
        ax1.plot(data.index, indicators['data_norm']['close'], label='Close Price', lw=0.5)
            
        ax1.plot(data.index, donc_up, label='Donchian Up', color='blue', lw=0.5)
        ax1.plot(data.index, donc_dn, label='Donchian Down', color='red', lw=0.5)
    # ax.plot(data.index, data['ema_filter'], label='Ema Filter', color='green', lw=1.5)
        ax1.plot(data.index, donch_mid, label='Donchian Mid', color='black', lw=0.5, linestyle='-')
        ax1.legend(loc='best')
        ax1.grid(axis='y')
        plt.show()
        return fig
    else:
        print('No Trades.')
        
#%%
# data.log_rets
# Proceed with optimizing and testing as before
optuna.logging.set_verbosity(optuna.logging.ERROR)
# asset = 'sp500'; exchange='indexes'; timeframe='1d'
# data = load_index_candles(asset)
# asset = 'Silver'; exchange='futures'; timeframe='1d'
# data = load_local_candles('./data',asset)
# data = data.resample(f'{7}D').agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
# Load the data
# asset = 'NVDA'
# data = load_sp500_stock_candles(asset)['2019':'2025']
# data['close'] = data['adj close']
# data = load_russel2000_candles('XOXO')['2006':]
# asset = 'NVDA'
# data = load_index_candles(asset)
### Cryptos - SPOT
asset, quote, timeframe, exchange = 'BTC', 'USDT', '4h', 'binance'
data = load_candles('binance',asset, quote, timeframe)['2020':'2025']#.iloc[-35000:-5000]
# data = data.sample(n=5000,replace=True).reset_index(drop=True)
# .assign(log_price=lambda df:df['close'].apply(np.log)
# ).assign(log_rets=lambda df:df.log_price.diff())
nhours = 9; train_ratio = 1;  long_short = 'long'
btargs = {'transaction_cost':0.001, 'slippage':0.003, 'precision':3, 'period_costs':0}
# data = data.resample(f'{nhours}H').agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
# data_train = data.iloc[:int(data.shape[0]*train_ratio)]; data_test = data.iloc[data.shape[0]:]
study = optimize_strategy(data, param_defs, calculate_indicators, signals_generator, skip_first_fn, btargs, long_short=long_short, n_trials=500, optimize_metrics=['tot_return', 'max_drawdown'])
aparams = [t.params for t in reversed(study.best_trials[-10:])]
# def custom_metric(metrics):
#     return metrics['overall_metrics']['tot_return'] / abs(metrics['overall_metrics']['max_drawdown'])
# study = optimize(
#   sortino  data,
#     nhours,
#     param_defs,
#     optimize_metrics=['overall_metrics.max_drawdown', 'short_metrics.profit_factor'],
#     directions=['maximize', 'maximize'],
#     n_trials=100
# )
# aparams = [t.params for t in reversed(study.best_trials[-10:])]
# print(f'aparams = {aparams}')
#%%

params = aparams[0]
print('params:')
pprint(params)
indicators = calculate_indicators(data, params)
entry_indices, exit_indices, metrics = comp_backtest(indicators,param_defs,params, signals_generator, long_short='long', skip_first_fn=skip_first_fn, flip_signal=False, btargs=btargs)
fig = plot_strategy(indicators,metrics,entry_indices,exit_indices,title=f'Asset: {asset}',convert_to_pct=True, mult_100=True)
plt.show()

#%%
for ipa, params in enumerate(aparams[:]):
    pprint(f'===================  {exchange} / {asset} / {timeframe} / params[ {ipa} ]  =================================')
    # print(f'params[ {ipa} ] = {params}')
    pprint(params)
    if len(data):
        indicators = calculate_indicators(data, params)
        
        print('--- LONG -----------------------------------------------------')
        entry_indices, exit_indices, metrics = comp_backtest(indicators,param_defs,params, signals_generator, long_short='long', skip_first_fn=skip_first_fn, flip_signal=False, btargs=btargs)
        fig = plot_strategy(indicators,metrics,entry_indices,exit_indices,title=f'Asset: {asset}',convert_to_pct=True, mult_100=True)
        plt.show()
        # if fig: fig.get_axes()[0].set_title(f'Asset: {asset}')
        # print('--- SHORT -----------------------------------------------------')
        # entry_indices, exit_indices, metrics = comp_backtest(indicators,param_defs,params, signals_generator, long_short='short', skip_first_fn=skip_first_fn, flip_signal=False, btargs=btargs)
        # fig = plot_strategy(indicators,metrics,entry_indices,exit_indices,title=f'Asset: {asset}',convert_to_pct=True, mult_100=True)
        # plt.show()
        # if fig: fig.get_axes()[0].set_title(f'Asset: {asset}')
        
#%%

asset, quote, timeframe, exchange = 'ETH', 'USDT', '4h', 'binance'
data = load_candles('binance',asset, quote, timeframe)['2020':'2025']
nhours = 9; train_ratio = 1;  long_short = 'long'
btargs = {'transaction_cost':0.001, 'slippage':0.003, 'precision':3, 'period_costs':0}

for ipa, params in enumerate(aparams[:]):
    pprint(f'===================  {exchange} / {asset} / {timeframe} / params[ {ipa} ]  =================================')
    # print(f'params[ {ipa} ] = {params}')
    pprint(params)
    if len(data):
        indicators = calculate_indicators(data, params)
        
        print('--- LONG -----------------------------------------------------')
        entry_indices, exit_indices, metrics = comp_backtest(indicators,param_defs,params, signals_generator, long_short='long', skip_first_fn=skip_first_fn, flip_signal=False, btargs=btargs)
        fig = plot_strategy(indicators,metrics,entry_indices,exit_indices,title=f'Asset: {asset}',convert_to_pct=True, mult_100=True)
        plt.show()
        
# params = aparams[1]
# print('params:')
# pprint(params)
# indicators = calculate_indicators(data, params)
# entry_indices, exit_indices, metrics = comp_backtest(indicators,param_defs,params, signals_generator, long_short='long', skip_first_fn=skip_first_fn, flip_signal=False, btargs=btargs)
# fig = plot_strategy(indicators,metrics,entry_indices,exit_indices,title=f'Asset: {asset}',convert_to_pct=True, mult_100=True)
# plt.show()

#
#%%