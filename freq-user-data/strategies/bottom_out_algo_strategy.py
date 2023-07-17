# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from typing import Optional, Union
from scipy.signal import find_peaks, peak_widths

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)


# Machine learning libraries
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# --------------------------------
# Add your lib to import here
# import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class BottomOutAlgoStrategy(IStrategy):
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
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = True

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '4h'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    # buy_rsi = IntParameter(low=1, high=50, default=30, space='buy', optimize=True, load=True)
    # sell_rsi = IntParameter(low=50, high=100, default=70, space='sell', optimize=True, load=True)
    # short_rsi = IntParameter(low=51, high=100, default=70, space='sell', optimize=True, load=True)
    # exit_short_rsi = IntParameter(low=1, high=50, default=30, space='buy', optimize=True, load=True)

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 100

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }

    plot_config = {
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        },
        'subplots': {
            "MACD": {
                'macd': {'color': 'blue'},
                'macdsignal': {'color': 'orange'},
            },
            "RSI": {
                'rsi': {'color': 'red'},
            }
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
        
        wdf['bod'] = wdf[['open', 'close']].min(axis=1)
        wdf['bou'] = wdf[['open', 'close']].max(axis=1)
        peak_dist = 5
        i_upeaks, _ = find_peaks(wdf.close, distance=peak_dist)
        ix_upeaks = wdf.index[i_upeaks]
        i_dpeaks, _ = find_peaks(-wdf.close, distance=peak_dist)
        ix_dpeaks = wdf.index[i_dpeaks]

        ###############################################################

        wdf['inow'] = range(wdf.shape[0])
        wdf['lret'] = wdf.close.divide(wdf.close.shift()).apply(np.log)
        a_last_peaks = np.array([
            # wdf.index.values[[idf, ipk]]
            [idf, ipk, *wdf.index[[idf, ipk]]]
            # [(idf, ipk), tuple(wdf.index[[idf, ipk]])]
            for ipk in i_upeaks

            for idf in list(range(ipk + 1, min(wdf.shape[0] - 1, ipk + 1 + int(peak_dist/2))))
        ]).T
        wdf.loc[a_last_peaks[2],'iupk'] = a_last_peaks[1]
        wdf.loc[a_last_peaks[2],'ixupk'] = a_last_peaks[3]

        wdf.loc[a_last_peaks[2],'n_upk'] = wdf.loc[a_last_peaks[2],'inow'] - a_last_peaks[1]

        wdf.loc[a_last_peaks[2], 'upk_close'] = wdf.loc[a_last_peaks[3]].close.values
        wdf.loc[a_last_peaks[2], 'upk_ret'] = wdf.loc[a_last_peaks[2], 'close'] / wdf.loc[a_last_peaks[2], 'upk_close']  - 1

        fus = [1,2,3,4,5,6]
        furet_cols = [f'furet_{fu}' for fu in fus]

        wdf = wdf.join(pd.concat([ wdf.close.shift(-fu) / wdf.close - 1 for fu in fus ], axis=1).set_axis(furet_cols, axis=1))

        lags = [2,3,4,6]
        la_cols = [f'bod_std_{la}' for la in lags]

        wdf = wdf.join(pd.concat([
            wdf.bod.rolling(la).std()
            for la in lags
            ],axis=1).set_axis(la_cols, axis=1))
        
        ##########################################################################
        tdf = wdf.dropna().copy()


        X = wdf[['upk_ret', 'n_upk', 'bod_std_6', 'bod_std_3', 'bod_std_2' ] ]

        y = np.where(wdf['furet_2'] < 0 , -1, 0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0, train_size=0.75)

        # Instantiate KNN learning model(k=15)
        knn = KNeighborsClassifier(n_neighbors=10)

        # fit the model
        knn.fit(X_train, y_train)

        y_hat = knn.predict(X)


        wdf['y_hat'] = y_hat

        return wdf

    def populate_entry_trend(self, wdf: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        wdf.loc[(wdf['y_hat'] < 0), 'enter_short'] = 1

        return wdf

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        dataframe.loc[:'exit_short'] = 1

        return dataframe
