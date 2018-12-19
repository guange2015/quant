import ccxt
from pprint import pprint
import pandas as pd
import numpy as np
import pdb
import json
import datetime

proxies = {
    'http': 'http://127.0.0.1:1087',
    'https': 'https://127.0.0.1:1087',
}

# symbol = 'EOS/USDT'
symbol = 'EOS/USDT'

#提现手续费1
#TODO 需要自行查网站设置
withDrawFee1 = 0.001
#提现手续费2
withDrawFee2 = 0.001

# 过滤阀值
min_threshold = 0
max_threshold = 100


def usage:
    print("交易对%s" % symbol)
    print("提现手续费 %f" % withDrawFee1)
    print("提现手续费 %f" % withDrawFee2)
    print("过滤阀值[%f, %f]" %(min_threshold, max_threshold))

usage()

datas = []

def progress(n,total):
    percent = round(1.0 * n / total * 100,2)
    print('当前进度 : %s [%d/%d]' % (str(percent)+'%',n+1,total),end='\r')

index = 0
for i in ccxt.exchanges:
    try:
        progress(index, len(ccxt.exchanges))
        index += 1
        exchange = getattr(ccxt, i)({'proxies': proxies})
        markets = exchange.load_markets()
        if symbol in markets:
            orders = exchange.fetch_order_book(symbol, limit=1)
            datas.append({
                'bids': orders['bids'],
                'asks': orders['asks'],
                'exchange': i
            })
    except Exception as e:
        # print(e)
        pass

now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')    

try:
    with open('/tmp/test_{0}.json'.format(now), 'w+') as f:
        f.write(json.dumps(datas))
except:
    print("write file error")
    pass

gf = None
for i in datas:
    df = pd.DataFrame(i['bids'])
    df = df.merge(pd.DataFrame(i['asks']), left_index=True, right_index=True)
    df['exchange'] = i['exchange']
    if len(df.columns)<5: continue
    if gf is None:
        gf = df
    else:
        gf = pd.concat([gf, df])


gf.columns = ['bid_price','bid_num', 'ask_price', 'ask_num', 'exchange']
gf = gf[(gf['bid_price']>min_threshold) & (gf['ask_price']<max_threshold) & (gf['exchange']!='hitbtc') & (gf['exchange']!='hitbtc2')]

#bid 买家愿意买的最高价
#ask 卖家愿意卖的最低价
maxBid = gf.sort_values(by='bid_price', ascending=False).head(5)
minAsk = gf.sort_values(by='ask_price', ascending=True).head(5)

# print(maxBid[['bid_price', 'exchange']])
# print (minAsk[['ask_price', 'exchange']])

maxBid['bid_price'] - minAsk.iloc[0]['bid_price']

# 最高卖出价 - (最低买入价 + 买入手续费 + 提现手续费 + 卖出手续费 + 提现手续费)
maxforSell = maxBid.iloc[0]['bid_price']
minForBuy  = minAsk.iloc[0]['ask_price']

def getTakerFee(exchange_name, symbol):
    exchange = getattr(ccxt, exchange_name)({'proxies': proxies})
    markets = exchange.load_markets()
    return markets[symbol]['taker']

def getMakerFee(exchange_name, symbol):
    exchange = getattr(ccxt, exchange_name)({'proxies': proxies})
    markets = exchange.load_markets()
    return markets[symbol]['maker']

takerFee = getTakerFee(minAsk.iloc[0]['exchange'], symbol)
makerFee = getMakerFee(maxBid.iloc[0]['exchange'], symbol)



print("最高卖出价%f 交易所 %s" % (maxforSell,maxBid.iloc[0]['exchange'] ) )
print("最低买入价%f 交易所 %s" % (minForBuy,minAsk.iloc[0]['exchange']))
print("买入手续费%f" % takerFee)
print("卖出手续费%f" % makerFee)
print("%s提现手续费%f" % (maxBid.iloc[0]['exchange'], withDrawFee1))
print("%s提现手续费%f" % (minAsk.iloc[0]['exchange'], withDrawFee2))

print('比值: %f' % (maxforSell- (minForBuy+takerFee+makerFee+withDrawFee1+withDrawFee2) ) )

