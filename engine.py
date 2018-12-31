# coding=utf-8
from base import Base
import pandas as pd


class Engine(Base):
    def __init__(self, balance=10000, maker_fee=0.002, taker_fee=0.002):
        """
        :param balance: 帐户余额
        :param maker_fee: 卖单拥金
        :param taker_fee: 买单拥金
        """
        names = ['id', 'open', "close", "low", "high", "amount", "vol", "count"]
        self.datas = pd.read_csv('datas/bchusdt.csv', names=names)
        times = pd.to_datetime(self.datas['id'], unit="s")
        self.datas.insert(0, 'time', times)
        self.context = None

        self.maker_fee = maker_fee
        self.taker_fee = taker_fee

        self.total_maker_cnt = 0
        self.total_taker_cnt = 0
        self.total_fee = 0

        self.myaccount = {
            "balance": balance,  # 余额
            "stocks": 0,  # 持仓
        }

        self.user_data = {}

        # 买入深度
        self.taker_depth = 0
        self.tmp_taker_depth = 0

    def buy(self, stock):
        """
        买入
        :param stock: 为0时全买入
        :return:
        """
        price = self.context['low']  # 当前最低价
        fee = price * self.taker_fee

        if stock == 0:
            stock = self.myaccount['balance'] / price

        money = price * stock

        if self.myaccount["balance"] - money - fee < 0:
            raise Exception("余额不足")

        self.total_taker_cnt += 1
        self.total_fee += fee

        self.myaccount["balance"] -= money
        self.myaccount["balance"] -= fee
        self.myaccount['stocks'] += stock

    def sell(self, stock):
        """
        卖出
        :param stock: 为0时，空仓
        :return:
        """
        price = self.context['high']  # 当前最低价
        fee = price * self.maker_fee

        if stock == 0:
            stock = self.myaccount["stocks"]

        if self.myaccount["stocks"] - stock < 0:
            raise Exception("仓位不足")

        self.total_maker_cnt += 1
        self.total_fee += fee

        money = stock * price

        self.myaccount["stocks"] -= stock
        self.myaccount["balance"] += money
        self.myaccount["balance"] -= fee

    def info(self):
        money = self.myaccount['balance'] + self.myaccount['stocks'] * self.context['high']
        print("余额: %f, 持仓: %f, 当前价格: %f, 价值 = %f, 买入单数: %d, 卖出单数: %d, 手续费: %f" %
              (self.myaccount['balance'], self.myaccount['stocks'],
               self.context['high'],
               money,
               self.total_taker_cnt, self.total_maker_cnt, self.total_fee))

    def tick(self, context):
        raise NotImplementedError("tick必须实现")

    def run(self):
        for i in range(len(self.datas)):
            if not self.datas.loc[i].empty:
                self.context = self.datas.loc[i].to_dict()
                self.tick(context=self.context)

        self.info()
