
import ccxt
import config
import schedule
import pandas as pd
pd.set_option('display.max_rows', None)
from datetime import datetime
import time
import pytz
import json

# import warnings
# warnings.filterwarnings('ignore')
import sys
sys.path.insert(1, './strategy')
from importlib import reload  

exchange = ccxt.kucoin({
    "apiKey": config.KUCOIN_API_KEY,
    "secret": config.KUCOIN_SECRET_KEY,
    "password": config.KUCOIN_API_PASSPHRASE
})


def run_bot():
    print(f'{datetime.now()} Checking for new orders...')
    odf = pd.read_csv ('order-data/orders.csv', index_col='id', dtype={'id': 'string', 'orderId': 'string'})
    ondf = odf[odf.orderId.isnull()]
    pairs = ondf.pair.values
    tickers = exchange.fetchTickers (pairs)

    for oind, orow in ondf.iterrows():
        # print("index", index)
        module = __import__(orow.strategy)
        order_class = getattr(module, orow.strategy)
        order_params = json.loads(orow.order_params)
        order_instance = order_class(exchange, orow.pair, tickers[orow.pair], order_params)
        order = order_instance.execute()
        if order:
            odf.loc[oind, "orderId"] = order['id']
            odf.to_csv('order-data/orders.csv', index=True)
    # odf


schedule.every(10).seconds.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)