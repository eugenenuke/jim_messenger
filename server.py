#!/usr/bin/env python3

import socket
import json
import time
import sys
import getopt

from jimm import *

class JIMSrv:

    MAX_CLIENTS = 5

    def __init__(self, addr, port):
        self._addr = addr
        self._port = port
        self._users = []
        self.actions = {
                'presence': self.action_presence
            }

    def add_user(self, user):
        self._users.append(user)

    def is_user_registered(self, user_name):
        for user in self._users:
            if user.get_name() == user_name:
                return True
        return False

    def action_presence(self, data):
        if self.is_user_registered(data['user']['account_name']):
            response = {
                        'response': 409,
                        'time': int(time.time()),
                        'error': 'User {} already registered!'.format(data['user']['account_name'])
                    }
        else:
            new_user = JIMUser(data['user']['account_name'])
            self.add_user(new_user)
            response = {
                        'response': 200,
                        'time': int(time.time()),
                        'alert': 'Welcome, {}!'.format(data['user']['account_name'])
                    }
        return response

    def server_loop(self, conn):
        request = json.loads(conn.recv(MAX_MESSAGE).decode())
        print(request)
        
        if request['action'] in self.actions:
            response = self.actions[request['action']](request)
        else:
            response = {
                        'response': 400,
                        'time': int(time.time()),
                        'error': 'Unknown action!'
                    }

        response = json.dumps(response).encode()
        conn.send(response)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_sock:
            try:
                main_sock.bind((self._addr, self._port))
                main_sock.listen(self.MAX_CLIENTS)

                while True:
                    conn, addr = main_sock.accept()
                    self.server_loop(conn)
                    conn.close()

            except Exception as e:
                print(e)



class JIMUser:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name


def check_opt(opt, opts, check):
    for row in opts:
        if opt == row[0]:
            return check(row[1])
    return False


def main():
    opts = getopt.getopt(sys.argv[1:], 'a:p:')[0]
    if not (check_opt('-a', opts, is_ip) and check_opt('-p', opts, port_is_num)):
        print('Usage: {} -p <port> -a <address>'.format(sys.argv[0]))
        sys.exit(BAD_OPTS)
    opts = dict(opts)
    addr = opts['-a']
    port = int(opts['-p'])

    jim = JIMSrv(addr, port)
    jim.start()


if __name__ == '__main__':
    main()
