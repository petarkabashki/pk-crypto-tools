
import pandas as pd
import numpy as np
import glob

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
    # df.index = df['time']
    # df.set_index('time', drop=True, inplace=True)
    odf['idate'] = odf.date.dt.strftime('%Y%m%d')
    odf.set_index(pd.DatetimeIndex(odf["date"]), inplace=True, drop=True)
    # df = df[['time', 'symbol', 'source', 'resolution', 'open', 'high', 'low', 'close', 'volume']]
    # df.to_csv (r'./data/binance/BTC_USDT-5m.csv', index = None)
    # df.set_index('time')
    odf = odf.sort_index()
    return odf
