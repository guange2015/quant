# coding=utf-8

## 采集火币数据


## 每30分钟采一次，period为1m

import json
import logging
import os
import time

import requests

api_key = None

proxies = {
    'http': 'http://localhost:1087',
    'https': 'http://localhost:1087'
}


def format_time(sec):
    timeArray = time.localtime(sec)  # 1970秒数
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def load_private_keys():
    """获取key
    Returns:
        ['api_key', 'api_secret']
    """
    global api_key
    f = open('key.json')
    content = f.read()
    f.close()
    config = json.loads(content)['huobipro']
    api_key = config['api_key']


def get_history_data(symbol, period='1min', size=40):
    url = "https://api.huobipro.com/market/history/kline?period={0}&size={1}&symbol={2}&" \
          "AccessKeyId={3}".format(period, size, symbol, api_key)
    res = requests.get(url, proxies=proxies)
    data = json.loads(res.text)

    file_path = "datas/{}.csv".format(symbol)
    ## 去重
    ids = []
    if os.path.exists(file_path):
        with open(file_path) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                try:
                    ids.append(line.split(',')[0])
                except Exception as e:
                    logging.error(e)

    clean_data = []
    for row in data["data"]:
        line = "{},{},{},{},{},{},{},{}\n".format(row["id"], row["open"], row["close"],
                                                  row["low"], row["high"], row["amount"],
                                              row["vol"], row["count"])
        if str(row["id"]) not in ids:
            clean_data.append(line)

    f = open(file_path, "a+")
    for line in clean_data:
        f.write(line)
    f.close()
    logging.info("{0}写入数据{1}条".format(file_path, len(clean_data)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s')  # logging.basicConfig
    load_private_keys()

    while True:
        for symbol in ['bchusdt', 'eosusdt', 'btcusdt', 'ethusdt']:
            try:
                get_history_data(symbol)
            except Exception as e:
                logging.error(e)
            time.sleep(10)
        time.sleep(20)
