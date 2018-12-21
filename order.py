# coding=utf-8
import json
import time
import ccxt
import logging

# 思路整理
# 1. 手工买入
# 2. 实时监控市价
# 3. 市价到达20%收益时，下发卖出市价单
# 4. 市价到达5%亏损时，下发卖出市价单


# 可配置变量
import notify

# proxies = {
#     'http': 'http://127.0.0.1:1087',
#     'https': 'https://127.0.0.1:1087',
# }

proxies = {
    'http': 'socks5://127.0.0.1:1086',
    'https': 'socks5://127.0.0.1:1086',
}


# 交易所
g_exchange_name = 'huobipro'
g_exchange = None

# 交易对
g_symbol = 'BCH/USDT'

# 购买价格
g_buy_price = 200.00


def load_private_keys():
    """获取key
    Returns:
        ['api_key', 'api_secret']
    """
    f = open('key.json')
    content = f.read()
    f.close()
    return json.loads(content)[g_exchange_name]


def init():
    global g_exchange

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s')  # logging.basicConfig

    key_config = load_private_keys()
    g_exchange = getattr(ccxt, g_exchange_name)({
        'proxies': proxies,
        'apiKey': key_config['api_key'],
        'secret': key_config['api_secret'],
    })


def monitor():
    """监控市价
        BID是买入价,买家愿意买的最高价
        ASK是卖出价,卖家愿意卖的最低价
    Returns:
          最低卖出
    """

    min_ask = 0
    try:
        orders = g_exchange.fetch_order_book(g_symbol, limit=1)
        if orders is not None:
            min_ask = orders["asks"][0][0]
    except Exception as e:
        logging.error("获取最低卖出价失败: {0}".format(e))
    return min_ask


def order():
    """
    下单
    :return:
    """
    type = 'market'
    side = 'buy'
    amount = 0.1
    price = 197.73

    ret = g_exchange.createOrder(g_symbol, type, side, amount, price)
    logging.info(ret)


def short():
    """空仓
        exchange.create_order(symbol, type, side, amount, price, params)
        type limit=>限价单. market=>市价单
        side buy=>买.  sell=>卖
        amount. 注意，这个值会自动精度化
        price.     只有限价单时才用得着
        params  交易所自带的私有属性
    """
    type = 'market'
    side = 'sell'

    amount = g_exchange.fetchBalance()[g_symbol.split('/')[0]]['free']

    logging.info('开始空仓: ')
    logging.info('amount: %f' % amount )

    ret = g_exchange.createOrder(g_symbol, type, side, amount)
    logging.info(ret)


def is_over_threshold():
    min_price = monitor()
    logging.info("当前价格: %f, 买入价: %f, 差额: %f, 比值: %f%%" % (min_price, g_buy_price, min_price-g_buy_price,
                                        (min_price-g_buy_price)*100/g_buy_price))
    if min_price> 0:
        if min_price-g_buy_price >= g_buy_price/5:    #收益大于 20%
            logging.info("收益价%f" % min_price)
            return True
        elif g_buy_price-min_price >= g_buy_price/20: #损失大于 5%
            logging.info("止损价%f" % min_price)
            return True
    return False


if __name__ == '__main__':
    init()
    try:
        while True:
            if is_over_threshold():
                short()
                break
            time.sleep(5)
    finally:
        notify.notify_by_dingding("平仓了，看看有没有赚到")
