import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from IPython.display import display
import glob
import json
from ipywidgets import interact, interactive, fixed, interact_manual
# import ipywidgets as widgets
from ipywidgets import *

def load_close_prices(exchange, coins, quote, time_frame, start_ts, end_ts):
    data_folder = f'../freq-user-data/data/{exchange}'

    data_files = [
        (f'{base}_{quote}-{time_frame}.json', base, quote)
        for base in coins
    ]
    # data_files
    df = pd.concat([
        pd.read_json(f'{data_folder}/{data_file}').set_index(0).loc[start_ts:end_ts, 4]
        for (data_file, base, quote) in data_files
    ], axis=1).set_axis(coins, axis=1
    ).assign(dt=lambda x: pd.to_datetime(x.index.values, unit='ms', utc=False)
    ).set_index('dt', drop=True
    ).sort_index()

    df.sort_index(inplace=True)
    return df

def load_candles(exchange, pair, timeframe):
    odf = pd.read_json(f'../../freq-user-data/data/{exchange}/{pair}-{timeframe}.json').dropna()
    odf.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

    odf['date'] = pd.to_datetime(odf['timestamp'], unit='ms', utc=False)
    odf['idate'] = odf.date.dt.strftime('%Y%m%d')
    odf.set_index(pd.DatetimeIndex(odf["date"]), inplace=True, drop=True)
    odf = odf.sort_index()
    return odf


def identify_axes(ax_dict, fontsize=48):
    kw = dict(ha="center", va="center", fontsize=fontsize, color="darkgrey")
    for k, ax in ax_dict.items():
        ax.text(0.5, 0.5, k, alpha=0.1, transform=ax.transAxes, **kw)


def plot_candles(wdf, ax=None, kwargs={}):
    # if ax is None:
    #     fig, ax = plt.subplots(**kwargs)

    up, down = wdf[wdf.close >= wdf.open], wdf[wdf.close < wdf.open]
    col1,col2 = 'green','red'
    width, width2 = 2, .1
    # Plotting up prices of the stock
    ax.bar(up.index, up.close-up.open, width, bottom=up.open, color=col1)
    ax.bar(up.index, up.high-up.close, width2, bottom=up.close, color=col1)
    ax.bar(up.index, up.low-up.open, width2, bottom=up.open, color=col1)
    # Plotting down prices of the stock
    ax.bar(down.index, down.close-down.open, width, bottom=down.open, color=col2)
    ax.bar(down.index, down.high-down.open, width2, bottom=down.open, color=col2)
    ax.bar(down.index, down.low-down.close, width2, bottom=down.close, color=col2)   

def get_fudf(wdf, fu):    
    fu_columns = [('high','max'), ('low','min'), ('close','mean')]
    fu_columns = [(f'fu_{c}_{f}', (c,f)) for c, f in fu_columns]
    fudf = pd.DataFrame(
        {
            fu_col: getattr(wdf[c].rolling(fu),f)()
            for (fu_col, (c, f)) in fu_columns
        }, index=wdf.index
        ).assign(**{f'ret_{fu_col}': lambda x: x[fu_col].divide(wdf.close) - 1
            for (fu_col, (_,_)) in fu_columns

        }).shift(-fu)
    return fudf

def fu_printer(odf, strategy, strategy_params = {}, indicator_func = None, signal_func = None, draw_func = None):

    strategy_params_json = f'./par-{strategy}.json'
    ### windowing
    olen = odf.shape[0]
    w2log = 7
    wlen = 2**w2log
    w2len = wlen // 2
    nwin = olen // w2len
    # olen, w2log, wlen, w2len, nwin
    ###
    fu_params = {
            'w2log':    {'wdg': IntSlider(description="n2", min=0, max=13, step=1, value=w2log)}, 
            'w':        {'wdg': IntSlider(description="w", min=0, max=nwin, step=1, value=1)},
            'inow':        {'wdg': IntSlider(description="inow", min=0, max=wlen-1, step=1, value=1)},
            "fu":       {'wdg': IntSlider(value=7,min=1,max=50,step=1,description='Hold',continuous_update=False)},
            "fu_lines": {'wdg': Checkbox(value=True, description='Fu lines', disabled=False)},
            "candles":  {"wdg": Checkbox(value=True, description='Candles', disabled=False)},
        }
    
    def update_sl_w_range(*args):
        wlen = 2**w2log
        w2len = wlen // 2
        nwin = olen // w2len
        fu_params['w']['wdg'].value = 0
        fu_params['w']['wdg'].max = nwin
        fu_params['inow']['wdg'].max = wlen * 2 -1
        fu_params['inow']['wdg'].value = wlen -1
    fu_params['w2log']['wdg'].observe(update_sl_w_range, 'value')

    all_params = {
        ** fu_params,
        **strategy_params
    }
    wdgts = [pv['wdg'] for pk, pv in all_params.items()]

    ui = widgets.VBox([
        widgets.VBox([widgets.HBox(wdgts[i:i+4]) for i in range(0, len(wdgts), 4)])
    ])

    if os.path.exists(strategy_params_json):
        with open(strategy_params_json) as f: 
            js = json.loads(f.read());
            for k, v in all_params.items(): 
                if k in js: v['wdg'].value=js[k];

    else: print(f'File not found: {strategy_params_json}')

    wdf=None
    def printer(**pkwargs):   
        w2log, w, fu, candles, fu_lines = pkwargs['w2log'], pkwargs['w'], pkwargs['fu'], pkwargs['candles'], pkwargs['fu_lines']

        wlen = 2**w2log
        w2len = wlen // 2
        nwin = olen // w2len

        with open(strategy_params_json, "w") as f: f.write(json.dumps({k: v['wdg'].value for k, v in all_params.items()}))
        
        
        wst = w * w2len
        wed = wst + wlen
        if olen - wed + 1 < w2len: wed = - 1
        # print(f'wst:{wst}, wed:{wed}')
        wdf = odf.iloc[wst:wed,:].copy()    
        # wlen = len(wdf)

        inow = pkwargs['inow']
        ixnow = wdf.index[inow]

        indicators = None
        if indicator_func is not None:
            indicators = indicator_func(**{'wdf': wdf, 'pkwargs': pkwargs})

        signals = None
        if signal_func is not None:
            # print('indicators', indicators)

            signals = signal_func(indicators, pkwargs)

        fudf = get_fudf(wdf, fu)

        print(f'N={len(wdf)}; Period: {wdf.index[-1] - wdf.index[0]}, Start: {wdf.index[0]}, End: {wdf.index[-1]}\n')
        print('plt.rcParam["lines.linewidth"]: ', plt.rcParams["lines.linewidth"])
        fig = plt.figure(layout="constrained", figsize=(12,6))
        ax_dict = fig.subplot_mosaic("""
            AAA
            BBB
            XYZ
            """,
            height_ratios=[3, 1, 1],
        )
        identify_axes(ax_dict)
        plt.xticks(rotation=30, ha='right')
        axa = ax_dict['A']
        axb = ax_dict['B']
        wdf.close.plot(ax=axa, lw=0.4, alpha=0.);

        if fu_lines: fudf[['fu_high_max', 'fu_low_min']].plot(ax=axa, lw=0.4);
        if candles: plot_candles(wdf, ax=axa);
        else: axa.plot(wdf.close, c='b');

        axa.axvline(ixnow, lw=3, c='m', alpha=0.5)

        if draw_func is not None: draw_func(ax_dict, indicators, signals, pkwargs)

        
        plt.show()
        
    out = widgets.interactive_output(printer, {
            **{k : v['wdg'] for k,v in all_params.items()}
        });
    x = display(ui, out);

