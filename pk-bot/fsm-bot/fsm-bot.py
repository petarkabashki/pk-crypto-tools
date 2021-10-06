#%%
from transitions import Machine
import enum 
import logging
import asyncio

from pymongo import MongoClient
from bson.objectid import ObjectId
import uuid
from pprint import pprint

from datetime import datetime
from math import floor, ceil

import sys
import zmq
import zmq.asyncio
# from s import Context
import json

logging.basicConfig(level=logging.INFO)

#%%
client = MongoClient()
db=client.fsmbot
# trades = {}
dbTrade = db.trades.find_one()

#%%
zContext = zmq.asyncio.Context()

class TradeModel(object):
    def __init__(self, dbTrade): 
        self.dbTrade = dbTrade
        self.symbol = 'ALGOUSDT'
        
        # self.set_environment()
    def removeCurrentStopOnExchange(self, event):
        print('removing current stop on exchange...')

    def buyTriggered(self, event):
        True
    
    def sellTriggered(self, event):
        True
    
    def runTicker(self, event):
        self.tickerTask = asyncio.create_task(self.subscribe2ticker())

    async def subscribe2ticker(self):
        tickerSocket = zContext.socket(zmq.SUB)
        tickerSocket.connect("tcp://localhost:5556")
        tickerSocket.setsockopt_string(zmq.SUBSCRIBE, self.symbol)
        while True:
            tickerString = await tickerSocket.recv_string()
            pprint(tickerString)
            ticker = json.loads(tickerString.split()[1])
            pprint(ticker)

        tickerSocket.close()

    def unsubscribe2ticker(self, event):
        pass
        # self.tickerSocket.close()

    def machineStateChange(self, event):
        db.trades.update_one({'_id' : dbTrade.get('_id') }, {
        '$set': {
            'state': self.state
          }})
        # print(json.dumps(event))

    async def run(self):
        while True:
            pass
    


tradeModel = TradeModel(dbTrade)


states = [
    'ERROR',
    'DISABLED',
    'LIVE',
    'LONG',
    'STOPPED',
    'DONE'
]

# transitions = [['start', 'DISABLED', 'LIVE'],
#                ['disable', 'LIVE', 'DISABLED'],
#                ['buy', 'LIVE', 'LONG'],
#                ['movestop', 'LONG', 'LONG'],
#                ['stopped', 'LONG', 'STOPPED'],
#                ['sell', 'LONG', 'DONE'],
#                ['error', '*', 'ERROR']]
transitions = [
    { 'trigger': 'start', 'source': 'DISABLED', 'dest': 'LIVE', 'before': 'runTicker'},
    { 'trigger': 'disable', 'source': 'LIVE', 'dest': 'DISABLED' , 'before': 'unsubscribe2ticker'},
    { 'trigger': 'tick', 'source': 'LIVE', 'dest': 'LONG', 'conditions': ['buyTriggered']},
    { 'trigger': 'movestop', 'source': 'LONG', 'dest': 'LONG' ,'before': 'removeCurrentStopOnExchange'},
    { 'trigger': 'stopped', 'source': 'LONG', 'dest': 'STOPPED'},
    { 'trigger': 'tick', 'source': 'LONG', 'dest': 'DONE' ,'before': 'removeCurrentStopOnExchange', 'conditions': ['sellTriggered']},
    # { 'trigger': 'error', 'source': 'liquid', 'dest': 'gas', 'after': 'disappear' }
]

async def main():
    machine = Machine(tradeModel, states=states, transitions=transitions, send_event=True, initial='DISABLED', after_state_change='machineStateChange')
    return  await tradeModel.run()
    # tradeModel.start()
    # tradeModel.disable()
    # tradeModel.start()

asyncio.run(main())

#%%

#%%
#%%
