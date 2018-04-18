#!/usr/bin/env python3

import json
import time
import logging
import argparse
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

    def _send_msg(self, msg, conn=None):
        if not conn:
            conn = self._conn
        data = json.dumps(msg).encode()
        try:
            conn.send(data)
        except BrokenPipeError as e:
            print(e)

    def _recv_msg(self, conn=None):
        if not conn:
            conn = self._conn

        try:
            data = conn.recv(MAX_MESSAGE)
        except Exception as e:
            print(e)

        if data:
            return json.loads(data.decode())
        return False

 
class JIMMsg:
    def __set__(self, instance, msg):
        data = {
                'action': 'msg',
                'time': time.time(),
                'to': instance._chat.get_name(),
                'from': instance._user,
                'message': msg
                }
        instance._send_msg(data)
        status = instance._recv_msg()
        try:
            instance._last_response = status
        except Exception:
            pass


class JIMResponse:
    def __set__(self, instance, data):
        (code, msg), client = data
        response = {
                    'response': code,
                    'time': time.time(),
                    'alert': msg
                }
        instance._send_msg(response, client)


class JIMChat():
    def __init__(self, chat_name='#default'):
        self._name = chat_name
        self._messages = []
        self._users = []

    def get_name(self):
        return self._name

    def add_message(self, msg, sender, time):
        self._messages.append({'msg': msg, 'from': sender, 'time': time})
        # print(self._messages)

    def get_all_messages(self):
        return self._messages


def is_ip(ip):
    octets = ip.split('.')
    if len(octets) == 4 and \
            all(el.isnumeric() and 0 <= int(el) < 256 for el in octets):
        return ip
    raise argparse.ArgumentTypeError(E_STRINGS['badip'])


def port_is_valid(num):
    if num.isnumeric() and 0 < int(num) < 65536:
        return int(num)
    raise argparse.ArgumentTypeError(E_STRINGS['badport'])
