import asyncio
import datetime
import json

import ccxt
import pandas as pd

# 可配置变量
proxies = {
    'http': 'http://127.0.0.1:1087',
    'https': 'https://127.0.0.1:1087',
}

# symbol = 'EOS/USDT'
symbol = 'EOS/USDT'

# 排除的交易所
exclude_exchanges = ['hitbtc', 'hitbtc2']

# 提现手续费1
# TODO 需要自行查网站设置
withdraw_fee1 = 0.001
# 提现手续费2
withdraw_fee2 = 0.001

# 过滤阀值
min_threshold = 0
max_threshold = 100

# 全局变量
g_datas = []
g_index = 0


#  函数定义
def init():
    global g_index
    g_datas.clear()
    g_index = 0


def progress(n, total):
    percent = round(1.0 * n / total * 100, 2)
    print('当前进度 : %s [%d/%d]' % (str(percent) + '%', n + 1, total), end='\r')


async def _fetch_order_book(exchange_name):
    global g_index
    try:
        exchange = getattr(ccxt, exchange_name)({'proxies': proxies})
        markets = exchange.load_markets()
        if symbol in markets:
            orders = exchange.fetch_order_book(symbol, limit=1)
            g_datas.append({
                'bids': orders['bids'],
                'asks': orders['asks'],
                'exchange': exchange_name
            })
        progress(g_index, len(ccxt.exchanges))
        g_index += 1
    except Exception as e:
        # print(e)
        pass


async def fetch_order_book(exchange_name):
    await _fetch_order_book(exchange_name)


def now_time():
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return now


def save_to_db(bid_exchange, ask_exchange, max_bid, min_ask, taker_fee, maker_fee, _withdraw_fee1,
               _withdraw_fee2,
               rate):
    """保存到csv文件
    Args:
        :param bid_exchange: 卖出的交易所
        :param ask_exchange: 买的交易所
        :param max_bid:  最高卖出价
        :param min_ask:  最低买入价
        :param taker_fee: 吃单手续费
        :param maker_fee: 挂单手续费
        :param _withdraw_fee1: 提取手续费1
        :param _withdraw_fee2: 提取手续费2
        :param rate: 比例

    """
    f = open('data.csv', 'a+')
    f.write(
        "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(now_time(), bid_exchange, ask_exchange,
                                                           max_bid, min_ask,
                                                           taker_fee, maker_fee, _withdraw_fee1,
                                                           _withdraw_fee2,
                                                           rate))
    f.close


def get_taker_fee(exchange_name, _symbol):
    """吃单费用"""
    exchange = getattr(ccxt, exchange_name)({'proxies': proxies})
    markets = exchange.load_markets()
    return markets[_symbol]['taker']


def get_maker_fee(exchange_name, _symbol):
    """挂单费用"""
    exchange = getattr(ccxt, exchange_name)({'proxies': proxies})
    markets = exchange.load_markets()
    return markets[_symbol]['maker']


def run_tasks_with_event_loop(tasks):
    old_loop = asyncio.get_event_loop()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    asyncio.set_event_loop(old_loop)


# 主函数
def start():
    init()
    print("交易对%s" % symbol)
    print("提现手续费 %f" % withdraw_fee1)
    print("提现手续费 %f" % withdraw_fee2)
    print("过滤阀值[%f, %f]" % (min_threshold, max_threshold))

    tasks = []
    for i in ccxt.exchanges:
        if i not in exclude_exchanges:
            tasks.append(fetch_order_book(i))

    run_tasks_with_event_loop(tasks)

    try:
        with open('/tmp/test_{0}.json'.format(now_time()), 'w+') as f:
            f.write(json.dumps(g_datas))
    except Exception as e:
        print("write file error", e)

    gf = None
    for i in g_datas:
        df = pd.DataFrame(i['bids'])
        df = df.merge(pd.DataFrame(i['asks']), left_index=True, right_index=True)
        df['exchange'] = i['exchange']
        if len(df.columns) < 5: continue
        if gf is None:
            gf = df
        else:
            gf = pd.concat([gf, df])

    gf.columns = ['bid_price', 'bid_num', 'ask_price', 'ask_num', 'exchange']
    gf = gf[(gf['bid_price'] > min_threshold) & (gf['ask_price'] < max_threshold)]

    # bid 买家愿意买的最高价
    # ask 卖家愿意卖的最低价
    max_bid = gf.sort_values(by='bid_price', ascending=False).head(5)
    min_ask = gf.sort_values(by='ask_price', ascending=True).head(5)

    # print(max_bid[['bid_price', 'exchange']])
    # print (min_ask[['ask_price', 'exchange']])

    max_bid['bid_price'] - min_ask.iloc[0]['bid_price']

    # 最高卖出价 - (最低买入价 + 买入手续费 + 提现手续费 + 卖出手续费 + 提现手续费)
    max_for_sell = max_bid.iloc[0]['bid_price']
    min_for_buy = min_ask.iloc[0]['ask_price']

    taker_fee = get_taker_fee(min_ask.iloc[0]['exchange'], symbol)
    maker_fee = get_maker_fee(max_bid.iloc[0]['exchange'], symbol)
    rate = max_for_sell - (min_for_buy + taker_fee + maker_fee + withdraw_fee1 + withdraw_fee2)
    bid_exchange_name = max_bid.iloc[0]['exchange']
    ask_exchange_name = min_ask.iloc[0]['exchange']

    save_to_db(bid_exchange_name, ask_exchange_name, max_for_sell, min_for_buy, taker_fee,
               maker_fee, withdraw_fee1,
               withdraw_fee2, rate)

    print("最高卖出价%f 交易所 %s" % (max_for_sell, bid_exchange_name))
    print("最低买入价%f 交易所 %s" % (min_for_buy, ask_exchange_name))
    print("买入手续费%f" % taker_fee)
    print("卖出手续费%f" % maker_fee)
    print("%s提现手续费%f" % (max_bid.iloc[0]['exchange'], withdraw_fee1))
    print("%s提现手续费%f" % (min_ask.iloc[0]['exchange'], withdraw_fee2))
    print('比值: %f' % rate)


if __name__ == '__main__':
    while True:
        try:
            start()
        except Exception as e:
            print(e)
