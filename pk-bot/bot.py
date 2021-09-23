#%%
import os
import ccxt
# import config
import schedule
import pandas as pd
pd.set_option('display.max_rows', None)
from datetime import datetime
import time
import pytz
import json
import numpy as np
# import warnings
# warnings.filterwarnings('ignore')
import sys
# sys.path.insert(1, './strategy')
from importlib import reload  
from pymongo import MongoClient
from bson.objectid import ObjectId
from pprint import pprint
#%%
exchanges = {}
config = False
with open ('config.json') as js: 
        config = json.load(js)

for exkey, exconf in config['exchanges'].items():
        if exconf['enabled'] and not exkey in exchanges:
                excred = exconf['cred']
                for crk, crv in excred.items():
                        if crv[0] == "$" : 
                                excred[crk] = os.getenv(crv[1:])

                exchanges[exkey] = getattr(ccxt, exkey) (excred)

#%%
client = MongoClient()
db=client.pkbot

tickers = {}

def run_bot():
  global exchanges, tickers
  
  print("Scanning for new orders ...")
  for csyms in db.xqueue.aggregate([    
      {'$match':{'status': "new"}},
      {'$unwind':"$q"},
      {'$group':{'_id': {'exchange':"$q.exchange", "symbol": "$q.symbol"}}},
      {'$group':{'_id': '$_id.exchange',"symbols": {'$addToSet': "$_id.symbol"}}},
      # {'$match':{'_id': qo['exchange']}}
  ]):
    exchange_name = csyms['_id']
    symbols = csyms['symbols']
    tickers[exchange_name] = exchanges[exchange_name].fetchTickers(symbols)
    # print(exchange_name, tickers[exchange_name])
  for qx in db.xqueue.find({'status' :'new'}):
    print(f"Processing q/{qx['_id']}")
    for idxqo, qo in enumerate(qx['q']):
      nqx = db.xqueue.find_one({'_id': qx.get('_id')})
      print(f'   qid/{qo["qid"]} status: {qo["status"]}')
      exchange_name = qo['exchange']
      symbol = qo['symbol']
      if qo['status'] != 'new':
        continue

      print(f'        Checking {exchange_name}: qid/{qo["qid"]} {qo["trigger"]}')
      
      exchange = exchanges[exchange_name]
      ticker = tickers[exchange_name][symbol]

      if not eval(qo['trigger'], {'ticker': ticker, 'qx' : nqx}):
        continue

      print(f'        Triggered {exchange_name}:  {qo["method"]}')
      # res = getattr(exchange, qo['method'])(*qo['margs'])
      res = eval(qo['method'])
      print('RES:', res)
      updres = db.xqueue.update_one({'_id' : qx.get('_id') }, {
        '$set': { 
          # f"q.{idxqo}.orderId": res['id'],
          f"q.{idxqo}.status": 'done',
          f"q.{idxqo}.res": res,
          }
      })

    if db.xqueue.find_one({'_id': qx.get('_id'), "q.status" : { "$ne": "done" }}) == None:
      db.xqueue.update_one({'_id' : qx.get('_id') }, {
          '$set': { 'status': 'done' }
        })


schedule.every(5).seconds.do(run_bot)
while True:
    schedule.run_pending()
    time.sleep(1)
# run_bot()