import logging
from transitions import Machine

from bson.objectid import ObjectId
# from transitions.extensions.asyncio import AsyncTimeout, AsyncMachine
# import datetime
from datetime import datetime

from dotmap import DotMap

trades = {}

states = [
    'ERROR',
    'DETACHED',
    'DISABLED',
    'LIVE',
    'LONG',
    'STOPPED',
    'SOLD'
]
transitions = [
    { 'trigger': 'start', 'source': 'DISABLED', 'dest': 'LIVE'},
    { 'trigger': 'disable', 'source': 'LIVE', 'dest': 'DISABLED'},
    { 'trigger': 'tick', 'source': 'LIVE', 'dest': 'LONG', 'conditions': 'is_buy_signal', 'before' : ['buy_on_exchange', 'loadrec', 'set_stop_on_exchange']},
    { 'trigger': 'movestop', 'source': 'LONG', 'dest': 'LONG' ,'before': ['saverec', 'loadrec', 'remove_stop_on_exchange', 'set_stop_on_exchange']},
    { 'trigger': 'tick', 'source': 'LONG', 'dest': 'STOPPED', 'conditions': 'is_stopped'},
    { 'trigger': 'tick', 'source': 'LONG', 'dest': 'SOLD' ,'conditions': 'is_sell_signal', 'before': ['remove_stop_on_exchange', 'sell_on_exchange']},
    { 'trigger': 'sell', 'source': 'LONG', 'dest': 'SOLD' , 'before': ['remove_stop_on_exchange', 'sell_on_exchange']},
    { 'trigger': 'update', 'source': '*', 'dest': None, 'before': 'saverec', 'after': 'loadrec'},
    { 'trigger': 'load', 'source': '*', 'dest': None, 'before': 'loadrec'},
    { 'trigger': 'save', 'source': '*', 'dest': None, 'before': 'saverec'},
    { 'trigger': 'insert', 'source': '*', 'dest': None, 'before': 'insertrec'},
    { 'trigger': 'attach', 'source': '*', 'dest': None, 'before': 'attachrec'}

]


class TradeModel(object):
    def __init__(self, exchange, db):
        logging.debug('TradeModel.__init__')
        self.db = db
        self.exchange = exchange
        self.rec = None
        self.machine = Machine(self, states=states, transitions=transitions, send_event=True, initial='DISABLED', 
            after_state_change=['machine_state_changed'], on_exception='handle_error')

    def attachrec(self, event):
        self.rec = DotMap(event.kwargs['data'])
        self.machine.set_state(self.rec.state)

        
    def loadrec(self, event):
        logging.debug(event.kwargs)
        self.rec = DotMap(self.db.find_one({'_id': ObjectId(self._id)}))
        self.state = self.rec.state


    def saverec(self, event):
        logging.debug(event.kwargs)
        try:
            self.db.update_one({'_id' : self._id }, event.kwargs['data'] )
        except BaseException as err:
            logging.error(err)
            self.db.update_one({'_id' : self._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})

    def insertrec(self, event):
        logging.debug(event.kwargs)        
        data = event.kwargs['data']
        try:
            datecreated = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            insertRes = self.db.insert_one({
                    "id": f"{data['symbol']}_{datecreated}",
                    "datecreated" : datecreated,
                    **data
                })
            self.rec = DotMap(self.db.find_one({'_id': insertRes.inserted_id}))
            self._id = insertRes.inserted_id
        except BaseException as err:
            logging.error(err)

    # def update_ticker(self, event):
    #     ticker = event.kwargs['ticker']
    #     self.ticker_price = ticker['curDayClose']

    def is_buy_signal(self, event):
        logging.debug(event.kwargs)
        ticker = event.kwargs['ticker']
        if float(ticker['curDayClose']) <= float(self.rec.trigger):
            return True
        return False

    def is_sell_signal(self, event):
        logging.debug(event.kwargs)
        ticker = event.kwargs['ticker']
        if float(ticker['curDayClose']) >= float(self.rec.target):
            return True
        return False

    def is_stopped(self, event):
        logging.debug(event.kwargs)
        ticker = event.kwargs['ticker']
        if float(ticker['curDayClose']) <= float(self.rec.stop):
            return True
        return False


    def buy_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            resp =self.exchange.create_order(self.rec.symbol, 'market', 'buy', float(self.rec.qty));
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'buyResp': resp
            }})
        except BaseException as err:
            logging.error(err)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})

    def sell_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            available_qty = self.rec.buyResp['filled'] - self.rec.buyResp['fee']['cost']
            resp =self.exchange.create_order(self.rec.symbol, 'market', 'sell', available_qty)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'sellResp': resp
            }})
        except BaseException as err:
            logging.error(err)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})

    def set_stop_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            available_qty = self.rec.buyResp['filled'] - self.rec.buyResp['fee']['cost']
            resp =self.exchange.create_order(self.rec.symbol, 'STOP_LOSS_LIMIT', 'sell', available_qty * 0.99, 
                0.90 * float(self.rec.stop), {'stopPrice': float(self.rec.stop),'type': 'stopLimit'})
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'curStopResp': resp
            }})
        except BaseException as err:
            logging.debug(err)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})

    def remove_stop_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            if self.rec.curStopResp:
                resp =self.exchange.cancel_order(self.rec.curStopResp['id'], symbol=self.rec.symbol)
                self.db.update_one({'_id' : self.rec._id }, {
                    '$set': {                        
                        'cancelStopResp': resp
                    }})
        
        except BaseException as err:
            logging.error(err)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})
      

    def machine_state_changed(self, event):
        # print(event.kwargs)
        logging.debug(event.kwargs)
        if None != self.rec:
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'state': self.state
            }})

    def handle_error(self, event):
        logging.debug(event.kwargs)
        logging.error(event.error)
        if None != self.rec:
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'error': { 
                    'error': event.error,
                    'kwargs': event.kwargs 
                    }
            }})

    def watch(self):
        symbol = self.rec.symbol
        if not symbol in trades: trades[symbol] = {}
        trades[symbol][str(self.rec._id)] = self

    def unwatch(self):
        trades[self.rec.symbol].pop(self.rec._id, None)




def load_trades(exchange, db):
    trades.clear()
    for trade in db.find():
        try:
            model = TradeModel(exchange, db)
            model.watch(trade)
        except BaseException as err:
            logging.error(err)          