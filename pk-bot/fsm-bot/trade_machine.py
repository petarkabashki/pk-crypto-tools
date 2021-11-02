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
    'LONG_OCO',
    'STOPPED',
    'TARGET',
    'SOLD'
]
transitions = [
    { 'trigger': 'start', 'source': 'DISABLED', 'dest': 'LIVE'},
    { 'trigger': 'disable', 'source': 'LIVE', 'dest': 'DISABLED'},
    { 'trigger': 'tick', 'source': 'LIVE', 'dest': 'LONG', 'conditions': 'is_buy_signal', 'before' : ['buy_on_exchange', 'loadrec', 'set_oco_on_exchange']},
    { 'trigger': 'moveoco', 'source': 'LONG_OCO', 'dest': 'LONG_OCO' ,'before': ['saverec', 'loadrec', 'cancel_oco_on_exchange', 'set_oco_on_exchange']},
    { 'trigger': 'canceloco', 'source': 'LONG_OCO', 'dest': 'LONG' ,'before': ['cancel_oco_on_exchange', 'loadrec']},
    { 'trigger': 'setoco', 'source': 'LONG', 'dest': 'LONG_OCO' ,'before': ['set_oco_on_exchange', 'loadrec']},
    # { 'trigger': 'tick', 'source': 'LONG', 'dest': 'LONG_OCO' ,'before': ['set_oco_on_exchange']},
    # { 'trigger': 'movetarget', 'source': 'LONG', 'dest': 'LONG' ,'before': ['saverec', 'loadrec', 'cancel_oco_on_exchange', 'set_oco_on_exchange']},
    { 'trigger': 'tick', 'source': 'LONG_OCO', 'dest': 'STOPPED', 'conditions': 'is_stopped'},
    { 'trigger': 'tick', 'source': 'LONG_OCO', 'dest': 'TARGET' ,'conditions': 'is_target'},
    { 'trigger': 'sell', 'source': 'LONG_OCO', 'dest': 'SOLD' , 'before': ['cancel_oco_on_exchange', 'sell_on_exchange']},
    { 'trigger': 'update', 'source': '*', 'dest': None, 'before': 'saverec', 'after': 'loadrec'},
    { 'trigger': 'load', 'source': '*', 'dest': None, 'before': 'loadrec'},
    # { 'trigger': 'save', 'source': '*', 'dest': None, 'before': 'saverec'},
    { 'trigger': 'delete', 'source': '*', 'dest': None, 'before': ['deleterec', 'unwatch']},
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

    def __str__(self):
        if self.rec:
            return f"{self.rec._id} {self.state} {self.rec.symbol} {self.rec.qty}"
        else:
            return f"{self.state}"


    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__() 
     
    def attachrec(self, event):
        self.rec = DotMap(event.kwargs['rec'])
        self.machine.set_state(self.rec.state)

        
    def loadrec(self, event):
        logging.debug(event.kwargs)
        self.rec = DotMap(self.db.find_one({'_id': ObjectId(self.rec._id)}))
        self.state = self.rec.state


    def saverec(self, event):
        logging.debug(event.kwargs)
        try:
            self.db.update_one({'_id' : self.rec._id }, event.kwargs['data'] )
        except BaseException as err:
            logging.error(err)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})


    def deleterec(self, event):
        logging.debug(f'deleting {self.rec._id} {self.rec.id}')
        try:
            self.db.delete_one({'_id' : self.rec._id })
            self.unwatch()
        except BaseException as err:
            logging.error(err)
            self.db.update_one({'_id' : self.rec._id }, {
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
        return False
        # ticker = event.kwargs['ticker']
        # if float(ticker['curDayClose']) >= float(self.rec.target):
        #     return True
        # return False

    def is_stopped(self, event):
        logging.debug(event.kwargs)
        ticker = event.kwargs['ticker']
        if float(ticker['curDayClose']) <= float(self.rec.stop):
            return True
        return False

    def is_target(self, event):
        logging.debug(event.kwargs)
        ticker = event.kwargs['ticker']
        if float(ticker['curDayClose']) >= float(self.rec.target):
            return True
        return False


    def is_error(self, event):
        logging.debug(event.kwargs)
        return 'err' in self.rec

    def buy_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            buyResp =self.exchange.create_order(self.rec.symbol, 'market', 'buy', float(self.rec.qty));
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'buyResp': buyResp,
                'availableQty': (buyResp['filled'] - buyResp['fee']['cost'])
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
            resp =self.exchange.create_order(self.rec.symbol, 'market', 'sell', self.rec['availableQty'] * 0.99)
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

    def set_oco_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            market = self.exchange.market(self.rec.symbol)
            # resp =self.exchange.create_order(self.rec.symbol, 'STOP_LOSS_LIMIT', 'sell', self.rec['availableQty'] * 0.99, 
            #     0.90 * float(self.rec.stop), {'stopPrice': float(self.rec.stop),'type': 'stopLimit'})
            resp = self.exchange.private_post_order_oco({
                'symbol': market['id'],
                'side': 'SELL',  # SELL, BUY
                'quantity': self.exchange.amount_to_precision(self.rec.symbol, self.rec.availableQty),
                'price': self.exchange.price_to_precision(self.rec.symbol, self.rec.target),
                'stopPrice': self.exchange.price_to_precision(self.rec.symbol, self.rec.stop),
                'stopLimitPrice': self.exchange.price_to_precision(self.rec.symbol, self.rec.stop * 0.95),  # If provided, stopLimitTimeInForce is required
                'stopLimitTimeInForce': 'GTC',  # GTC, FOK, IOC
                # 'listClientOrderId': exchange.uuid(),  # A unique Id for the entire orderList
                # 'limitClientOrderId': exchange.uuid(),  # A unique Id for the limit order
                # 'limitIcebergQty': exchangea.amount_to_precision(symbol, limit_iceberg_quantity),
                # 'stopClientOrderId': exchange.uuid()  # A unique Id for the stop loss/stop loss limit leg
                # 'stopIcebergQty': exchange.amount_to_precision(symbol, stop_iceberg_quantity),
                # 'newOrderRespType': 'ACK',  # ACK, RESULT, FULL
            })
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'oco': resp
            }})
        except BaseException as err:
            logging.debug(err)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})

    def cancel_oco_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            if self.rec.oco:
                resp = self.exchange.privateDeleteOrderList({'symbol': self.rec.market, 'orderListId': self.rec.oco.orderListId})
                # exchange.cancel_order(self.rec.curStopResp['orders'][0]['id'], symbol=self.rec.symbol)
                self.db.update_one({'_id' : self.rec._id }, {
                    '$set': {                        
                        'cancelOCO': resp
                    }})
        
        except BaseException as err:
            logging.error(err)
            self.db.update_one({'_id' : self.rec._id }, {
            '$set': {
                'state': 'ERROR',
                'err': str(err)
            }})
  
    def remove_stop_on_exchange(self, event):
        logging.debug(event.kwargs)
        try:
            if self.rec.curStopResp:
                resp =self.exchange.cancel_order(self.rec.curStopResp['orders'][0]['id'], symbol=self.rec.symbol)
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
                    # 'kwargs': event.kwargs 
                    }
            }})

    def watch(self):
        market = self.rec.market
        if not market in trades: trades[market] = {}
        trades[market][str(self.rec._id)] = self

    def unwatch(self):
        trades[self.rec.market].pop(self.rec._id, None)


# def get_trades():
#     return trades

def load_trades(exchange, db):
    trades.clear()
    for trade in db.find():
        try:
            model = TradeModel(exchange, db)
            model.attach(rec=trade)
            model.watch()
        except BaseException as err:
            logging.error(err)
    return trades