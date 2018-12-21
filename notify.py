#coding=utf-8

# 通知功能

import requests

_DING_NOTIFY_URL = 'https://oapi.dingtalk.com/robot/send?access_token=dfb3f45fdd33d3456d955871095121b985476b6016030ebb948bbe15e4a05aca'


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