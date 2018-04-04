#!/usr/bin/env python3


MAX_MESSAGE = 1024
BAD_OPTS = 1
E_STRINGS = {
        'badip': 'IP-адрес имеет неверный формат',
        'badport': 'port имеет неверный формат',
        'badargs': 'Неверно заданы аргументы'
        }


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
