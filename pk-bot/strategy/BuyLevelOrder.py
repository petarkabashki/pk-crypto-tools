import json

class BuyLevelOrder:

    def __init__(self, exchange, pair, ticker, order_params) -> None:

        # print('config:', config)
        self.pair = pair
        # self.config = config
        self.order_params = order_params
        self.exchange = exchange
        self.ticker = ticker
        # Dict to determine if analysis is necessary
        # self._last_candle_seen_per_pair: Dict[str, datetime] = {}
        # super().__init__(config)

    def execute(self):
        if self.ticker['ask'] <= self.order_params['trigger_price']:
            print(f'{self.__class__.__name__} triggered for pair {self.pair} with order_params {json.dumps(self.order_params)}' )
            order = self.exchange.create_market_buy_order(self.pair, self.order_params['qty'])
            return order
        # pass
        # print('order params:', self.order_params)
