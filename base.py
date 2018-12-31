#coding=utf-8
import logging
import json
import ccxt


class Base(object):

    proxies = {
        'http': 'http://127.0.0.1:1087',
        'https': 'https://127.0.0.1:1087',
    }

    def __init__(self, exchange_name, symbol):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s')  # logging.basicConfig
        self.symbol = symbol

        key_config = self.load_private_keys(exchange_name)
        self.exchange = getattr(ccxt, exchange_name)({
            'proxies': self.proxies,
            'apiKey': key_config['api_key'],
            'secret': key_config['api_secret'],
        })

    def account_info(self):
        return self.exchange.fetchBalance()

    @staticmethod
    def load_private_keys(exchange_name):
        """获取key
        Returns:
            ['api_key', 'api_secret']
        """
        f = open('key.json')
        content = f.read()
        f.close()
        return json.loads(content)[exchange_name]

