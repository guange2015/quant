from move_block import *


def test_now_time():
    print(now_time())
    assert now_time().startswith('2018')


def test_get_taker_fee():
    assert 0.002 == get_taker_fee('huobipro', 'EOS/USDT')