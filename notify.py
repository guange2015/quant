# coding=utf-8

# 通知功能

import requests

import config

_DING_NOTIFY_URL = 'https://oapi.dingtalk.com/robot/send?access_token=' \
                   + config.get_string('notify', 'ding_token')


def notify_by_dingding(msg):
    """
    使用钉钉发送通知消息
    :return:
    """
    send_obj = {
        "msgtype": 'text',
        'text': {
            'content': msg
        }
    }
    requests.post(_DING_NOTIFY_URL, json=send_obj)


if __name__ == '__main__':
    notify_by_dingding('币价涨了')
