I need to create a python mcp server tool to handle downloads via freqtrade. It should execute a terminal command in the form of 
`freqtrade download-data --userdir ./freq-user-data --data-format-ohlcv json --exchange binance -t 3d 1d 8h 4h 2h 1h 1w --timerange=20200101-  -p BTC/USDT ETH/USDT BNB/USDT SOL/USDT XRP/USDT ADA/USDT AVAX/USDT DOGE/USDT LINK/USDT TRX/USDT DOT/USDT MATIC/USDT TON/USDT ICP/USDT SHIB/USDT`
The userdir, exchange, timeframes and pairs should be parameters to the mcp tool.
