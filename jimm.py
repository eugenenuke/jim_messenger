#!/usr/bin/env python3

import json
import logging
from functools import wraps

import log_config

MAX_MESSAGE = 1024
BAD_OPTS = 1
E_STRINGS = {
        'badip': 'IP-адрес имеет неверный формат',
        'badport': 'port имеет неверный формат',
        'badargs': 'Неверно заданы аргументы'
        }

app_log = logging.getLogger('jimm')


def logger(msg):
    def decorator(func):
        # @wraps(func)
        def wrap(*args, **kwargs):
            app_log.debug('%s %s %s %s', func.__name__, msg, args, kwargs)
            ret = func(*args, **kwargs)
            return ret
        return wrap
    return decorator


class JIM:
    def __init__(self, addr, port):
        self._addr = addr
        self._port = port
        self._conn = None

    def send_msg(self, msg, conn=None):
        if not conn:
            conn = self._conn
        data = json.dumps(msg).encode()
        try:
            conn.send(data)
        except BrokenPipeError as e:
            print(e)

    def recv_msg(self, conn=None):
        if not conn:
            conn = self._conn

        try:
            data = conn.recv(MAX_MESSAGE)
        except Exception as e:
            print(e)

        if data:
            return json.loads(data.decode())
        return False


def is_ip(ip):
    octets = ip.split('.')
    if len(octets) == 4 and \
            all(el.isnumeric() and 0 <= int(el) < 256 for el in octets):
        return True
    print(E_STRINGS['badip'])
    return False


def port_is_valid(num):
    if num.isnumeric() and 0 < int(num) < 65536:
        return True
    print(E_STRINGS['badport'])
    return False
