# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter

# --------------------------------
# Add your lib to import here
# import talib.abstract as ta
import pandas_ta as ta

import freqtrade.vendor.qtpylib.indicators as qtpylib

from math import *
import json

from numpy import nan as npNaN

ijsconf = False
with open('strat-params-supertrend.json') as f: 
    ijsconf = json.loads(f.read());

print("ijsconf: ", ijsconf)
w2log=14;w=5;stn=18;stmu=3.0;bbman=21;bbstn=21;bbstd=0.7;adxn=21;adxdiff=0.0;adxtr=-3.0;adxmp=24.0;adxmn=16.0;sl=-0.03;tp=1.0;spg=0.001
# This class is a sample. Feel free to customize it.
class SupertrendStrategy(IStrategy):
    """
    This is a sample strategy to inspire you.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_buy_trend, populate_sell_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2


    # ROI table:
    minimal_roi = {
        "0": ijsconf['tp'],
        "1": ijsconf['tp'],
    }

    # Stoploss:
    stoploss = ijsconf['sl']

    # Trailing stop:
    # trailing_stop = True
    # trailing_stop_positive = 0.142
    # trailing_stop_positive_offset = 0.232
    # trailing_only_offset_is_reached = False

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    # sell_profit_only = False
    # ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = max(ijsconf['stn'], ijsconf['bbstn'], ijsconf['adxn'], ijsconf['bbman'])

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    plot_config = {
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        },
        'subplots': {
            # "MACD": {
            #     'macd': {'color': 'blue'},
            #     'macdsignal': {'color': 'orange'},
            # },
            # "RSI": {
            #     'rsi': {'color': 'red'},
            # }
        }
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, wdf: DataFrame, metadata: dict) -> DataFrame:
        

        wdf['hl2'] = (wdf.high + wdf.low) / 2
        high_low = wdf.high - wdf.low
        high_close = np.abs(wdf.high - wdf.close.shift())
        low_close = np.abs(wdf.low - wdf.close.shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        wdf['tr'] = np.max(ranges, axis=1)
        wdf['atr'] = wdf.tr.ewm(span=stn,min_periods=0,adjust=False,ignore_na=False).mean()
        # rolling(stn).mean()
        wdf['matr'] = stmu * wdf['atr']

        wdf['st_bub'] = wdf.hl2 + wdf.matr
        wdf['st_blb'] = wdf.hl2 - wdf.matr

        # Calculate Supertrend
        m = wdf.close.size
        dir_, trend = [1] * m, [0] * m
        long, short = [npNaN] * m, [npNaN] * m

        upperband = wdf.st_bub.values
        lowerband = wdf.st_blb.values
        close = wdf.close.values

        for i in range(1, m):
            if close[i] > upperband[i - 1]:
                dir_[i] = 1
            elif close[i] < lowerband[i - 1]:
                dir_[i] = -1
            else:
                dir_[i] = dir_[i - 1]
                if dir_[i] > 0 and lowerband[i] < lowerband[i - 1]:
                    lowerband[i] = lowerband[i - 1]
                if dir_[i] < 0 and upperband[i] > upperband[i - 1]:
                    upperband[i] = upperband[i - 1]

            if dir_[i] > 0:
                trend[i] = long[i] = lowerband[i]
            else:
                trend[i] = short[i] = upperband[i]

        wdf['st_trend'] = trend
        wdf['st_dir'] = dir_
        wdf['st_lower'] = long
        wdf['st_upper'] = short

        wdf['bb_std'] = wdf.close.rolling(bbstn).std()

        wdf['bb_middle'] = wdf.close.ewm(span=bbman,min_periods=0,adjust=False,ignore_na=False).mean()
        wdf['bb_std_bw'] = wdf.bb_std * bbstd
        wdf['bb_lower'] = wdf['bb_middle'] + wdf.bb_std_bw
        wdf['bb_upper'] = wdf['bb_middle'] - wdf.bb_std_bw
        wdf["bb_percent"] = (
            (wdf["close"] - wdf["bb_lower"]) /
            (wdf["bb_upper"] - wdf["bb_lower"])
        )
        wdf["bb_width"] = (
            (wdf["bb_upper"] - wdf["bb_lower"]) / wdf["bb_middle"]
        )

        wadf = ta.adx(wdf.high, wdf.low, wdf.close, length=adxn, lensig=None, mamode=None, scalar=None, drift=None, offset=None)
        wadf.columns = ['adx','dmp','dmn']
        wadf['dm_diff'] = wadf['dmp'].values - wadf['dmn'].values

        wdf = wdf.join(wadf)

        return wdf

    def populate_buy_trend(self, wdf: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """

        
        buy_cond = (
            (wdf.close <= wdf.bb_lower) &
            (wdf.adx >= adxtr) & 
            (wdf.dm_diff > adxdiff) & 
            (wdf.dmp >= adxmp) & 
            (wdf.dmn <= adxmn) &
            (wdf.st_dir == 1) #&
            # (wdf.st_dir.shift() == -1) 
        )
        # buy_cond = buy_cond.shift(fill_value=False)

        # buy_sig = (buy_cond & ((~buy_cond).shift(fill_value=False)))
        
        wdf.loc[
            buy_cond,
            'buy'] = 1
        # print('buy sig len:', len(dataframe[dataframe.buy == 1]))
        return wdf

    def populate_sell_trend(self, wdf: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with sell column
        """
        sell_cond = (
            (wdf.st_dir == -1) &
            (wdf.st_dir.shift() == +1) 
        )

        wdf.loc[
            (
                sell_cond
            ),
            'sell'] = 1
    
        return wdf
