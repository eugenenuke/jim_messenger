#!/usr/bin/env python3

import argparse
import socket
import random
import select
import json
import time
import sys

from jimm import *


class JIMClient(JIM):
    def __init__(self, addr, port):
        super().__init__(addr, port)
        self._user = 'User_{}'.format(random.randint(0, 9999))
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._conn.connect((self._addr, self._port))
        except ConnectionRefusedError as e:
            print(e)
            sys.exit(1)

    def send_quit(self):
        data = {
                'action': 'quit',
                }

        self.send_msg(data)

    @logger('Client is connecting to the server')
    def send_presence(self):
        data = {
                'action': 'presence',
                'time': time.time(),
                'type': 'status',
                'user': {
                        'account_name': self._user,
                        'status': 'I\'m here!'
                    }
                }

        self.send_msg(data)
        status = self.recv_msg()

        # print(status)
        return status

    def send_to_chat(self, msg, chat='#default'):
        data = {
                'action': 'msg',
                'time': time.time(),
                'to': chat,
                'from': self._user,
                'message': msg
                }
        # print(data)
        self.send_msg(data)
        status = self.recv_msg()
        # print(status)

        return status

    def get_message(self):
        msg = self.recv_msg()
        if msg['action'] == 'msg':
            print('{}: {}'.format(msg['from'], msg['message']))

    def get_conn(self):
        return self._conn

    def disconnect(self):
        self._conn.close()


@logger('Client has started')
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('addr', help='server\' address')
    parser.add_argument('port', nargs='?', default=7777, type=int, help='server\' port')
    parser.add_argument('-w', action='store_true', help='sends messages to the server')
    parser.add_argument('-r', action='store_true', help='reads messages from the server')
    args = parser.parse_args()

    addr = args.addr
    port = args.port

    if not port_is_valid(str(port)):
        port = None
        
    if not (is_ip(addr) and port):
        print(E_STRINGS['badargs'])
        print('Usage: {} <address> [<port>] [-w] [-r]'.format(sys.argv[0]))
        sys.exit(BAD_OPTS)

    clnt = JIMClient(addr, port)

    clnt.send_presence()
    if args.w:
        print('Type a message (\'\q\' for quit):')
        while True:
            msg = input('> ')
            if msg == '\q':
                break
            clnt.send_to_chat(msg)
    elif args.r:
        print('Waiting for messages (\'\q\' for quit)')
        kb_int = 0
        while not kb_int:
            read_lst, _, _, = select.select([clnt.get_conn(), sys.stdin], [], [], 0.2)
            for conn in read_lst:
                if conn is sys.stdin:
                    if input() == '\q':
                        kb_int = 1
                else:
                    clnt.get_message()

    clnt.send_quit()
    clnt.disconnect()


if __name__ == '__main__':
    main()
