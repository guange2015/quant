# coding=utf-8

"""
配置文件工具类
"""
import configparser

_config = None
CONFIG_FILE = 'config.cfg'


def _load_config():
    global _config
    if not _config:
        _config = configparser.ConfigParser()
        _config.read(CONFIG_FILE)
    return _config


def get_int(section, key):
    return _load_config().getint(section=section, option=key)


def get_float(section, key):
    return _load_config().getfloat(section=section, option=key)


def get_string(section, key):
    return _load_config().get(section=section, option=key)


def get_bool(section, key):
    return _load_config().getboolean(section=section, option=key)


def write_value(section, key, val):
    config = _load_config()
    config.set(section, key, val)
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
