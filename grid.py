import logging
import time

import engine
from base import Base


class Grid(Base):

    def __init__(self, exchange_name, symbol):
        super(Grid, self).__init__(exchange_name, symbol)
        self.base_line = 150.0  # 当前价格基准线
        self.one_hand = 0.2  # 一手买多少

    def sell(self, amount, price):
        """
        :param price: 定价
        :param stock_num: 量
        :return:

        exchange.create_order(symbol, type, side, amount, price, params)
        type limit=>限价单. market=>市价单
        side buy=>买.  sell=>卖
        amount. 限价单表示下单数量，市价买单时表示买多少钱（此时最大精度固定为8），市价卖单时表示卖多少币
        price.     只有限价单时才用得着
        params  交易所自带的私有属性
        """
        self.exchange.create_order(self.symbol, 'limit', 'sell', amount, price)

    def buy(self, amount, price):
        self.exchange.create_order(self.symbol, 'limit', 'buy', amount, price)

    def get_current_price(self):
        """监控市价
            BID是买入价,买家愿意买的最高价
            ASK是卖出价,卖家愿意卖的最低价
        Returns:
              [最高买价，最低卖价]
        """
        min_ask = 0
        max_bid = 0
        try:
            orders = self.exchange.fetch_order_book(self.symbol, limit=1)
            if orders is not None:
                min_ask = orders["asks"][0][0]
                max_bid = orders["bids"][0][0]
        except Exception as e:
            logging.error("获取最低卖出价失败: {0}".format(e))
        return max_bid, min_ask

    def run(self):
        # 获取当前价格
        self.print_account_info()
        max_bid, min_ask = self.get_current_price()
        rate1 = (self.base_line - min_ask) / self.base_line * 100
        rate2 = (max_bid - self.base_line) / self.base_line * 100
        logging.info("当前基线:%f, 最高买价:%f[%f]，最低卖价:%f[%f]"
                     % (self.base_line, max_bid, rate1, min_ask, rate2))
        # 如果比基准价格下降 5%, 购买一股
        if rate1 >= 5.0:
            self.buy(self.one_hand, min_ask)
            self.base_line = min_ask
        # 如果比基准价格高 5%, 抛出一股
        if rate2 >= 5.0:
            self.sell(self.one_hand, max_bid)
            self.base_line = max_bid

    def print_account_info(self):
        balances = self.account_info()
        logging.info("usdt: {0}".format(balances['USDT']))
        logging.info("bch: {0}".format(balances['BCH']))

    def test(self):
        print(self.exchange.fetchBalance())
        orders = self.exchange.fetch_order_book(self.symbol, limit=1)
        print(orders)
        print(self.get_current_price())
        self.print_account_info()


class BackToTestGrid(engine.Engine):
    def tick(self, context):
        # 下跌买入，上涨抛出
        last_context = self.user_data.get('last_context')
        if last_context is None:
            if context['high'] < 220:
                last_context = context
                self.user_data['last_context'] = context

        if last_context is None:
            return

        if context['high'] - last_context['high'] > last_context['high'] / 20:  # 上涨5%卖
            print("{0}-以{1}价格卖出".format(context['time'], context['low']))
            self.sell(10)
            self.user_data['last_context'] = context
        elif last_context['high'] - context['high'] > last_context['high'] / 20:  # 下跌5%买
            print("{0}-以{1}价格买入".format(context['time'], context['high']))
            self.buy(10)
            self.user_data['last_context'] = context


if __name__ == '__main__':
    grid = Grid('huobipro', 'BCH/USDT')
    while True:
        grid.run()
        time.sleep(3)
