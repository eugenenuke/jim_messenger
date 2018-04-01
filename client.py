#!/usr/bin/env python3

import socket
import json
import time
import sys

from jimm import *


def main():

    port = 7777

    if len(sys.argv) == 3 and not port_is_num(sys.argv[2]):
        port = None
        
    if not (1 < len(sys.argv) < 4 and is_ip(sys.argv[1]) and port):
        print(E_STRINGS['badargs'])
        print('Usage: {} <address> [<port>]'.format(sys.argv[0]))
        sys.exit(BAD_OPTS)

    if len(sys.argv) == 3:
        port = int(sys.argv[2])
    addr = sys.argv[1]

    data = {
            'action': 'presence',
            'time': int(time.time()),
            'type': 'status',
            'user': {
                    'account_name': 'TestUser',
                    'status': 'I\'m here!'
                }
            }
    data = json.dumps(data).encode()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cl_sock:
        try:
            cl_sock.connect((addr, port))
            cl_sock.send(data)

            data = cl_sock.recv(MAX_MESSAGE).decode()

            cl_sock.close()
        except Exception as e:
            print(e)

    print(data)


if __name__ == '__main__':
    main()
