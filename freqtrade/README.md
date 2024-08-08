## Bactest

# Spot binance

freqtrade backtesting --strategy IchimokuStrategy --data-format-ohlcv json -d /media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance -c user_data/config-binance-spot.json --timeframe 1d -p ALGO/USDT

freqtrade plot-dataframe --strategy IchimokuStrategy -d /media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance -c user_data/config-binance-spot.json -p ALGO/USDT --timeframe 1d 