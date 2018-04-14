#!/usr/bin/env python3

import socket
import json
import time
import sys
import getopt
import select
import logging

from jimm import *


class JIMChat():
    def __init__(self, name):
        self._name = name
        self._messages = []
        self._users = []

    def add_message(self, msg, sender, time):
        self._messages.append({'msg': msg, 'from': sender, 'time': time})
        # print(self._messages)

    def get_all_messages(self):
        return self._messages


class JIMServer(JIM):

    MAX_CLIENTS = 5
    # Also see 'actions' dict at the end of the class

    def __init__(self, addr, port):
        super().__init__(addr, port)
        self._users = []
        self._clients = []
        self._chats = {}
        self._chats['#default'] = JIMChat('#default')

    def add_message(self, msg, chat, sender, time):
        self._chats[chat].add_message(msg, sender, time)

    def add_user(self, user):
        self._users.append(user)
        # Adds user to a chat ...

    def is_user_registered(self, user_name):
        for user in self._users:
            if user.get_name() == user_name:
                return True
        return False
    
    @logger('New client has connected')
    def add_client(self, conn):
        self._clients.append(conn)

    @logger('A client has disconnected')
    def remove_client(self, conn):
        self._clients.remove(conn)
        conn.close()

    def get_clients(self):
        return self._clients

    @staticmethod
    def _resp(code, msg):
        response = {
                    'response': code,
                    'time': time.time(),
                    'alert': msg
                }
        return response

    @logger('Server is responding for the `presence` action.')
    def action_presence(self, data, conn):
        if self.is_user_registered(data['user']['account_name']):
            response = self._resp(409, 'User {} already registered!'.format(data['user']['account_name']))
        else:
            new_user = JIMUser(data['user']['account_name'], conn)
            self.add_user(new_user)
            response = self._resp(200, 'Welcome, {}!'.format(data['user']['account_name']))
        return response

    def action_msg(self, data, conn):
        if self.is_user_registered(data['from']):
            response = self._resp(200, 'Message was accepted.')
            for client in self._clients[2:]:
                if client != conn:
                    self.send_msg(data, client)
                    # should a client answer?
        else:
            response = self._resp(401, 'You have to login.')
        return response

    def action_quit(self, data, conn):
        for user in self._users:
            if user.get_conn() == conn:
                self._users.remove(user)
                break
        # Remove user from all chats

    def close_all(self):
        for client in self._clients[2:]:
            client.close()

    @logger('Server is listening for new connections')
    def start(self):
        print('Server is started (\'\q\' for quit)')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_sock:
            try:
                main_sock.bind((self._addr, self._port))
                main_sock.listen(self.MAX_CLIENTS)
            except Exception as e:
                print(e)

            self.add_client(main_sock)
            self.add_client(sys.stdin)

            kb_int = 0
            while not kb_int:
                read_lst = []
                read_lst, _, _, = select.select(self.get_clients(), [], [], 1)

                for client in read_lst:
                    if client is main_sock:
                        conn, addr = main_sock.accept()
                        self.add_client(conn)
                    elif client is sys.stdin:
                        if input() == '\q':
                            kb_int = 1
                    else:
                        request = self.recv_msg(client)
                        if request:
                            print(request)
                            
                            if request['action'] in self.actions:
                                response = self.actions[request['action']](self, request, client)
                            else:
                                response = self._resp(400, 'Unknown action!')
                            if response:
                                response = self.send_msg(response, client)
                        else:
                            self.remove_client(client)
            self.close_all()
                

    actions = {
            'presence': action_presence,
            'msg': action_msg,
            'quit': action_quit
        }


class JIMUser:
    def __init__(self, name, conn):
        self._conn = conn
        self._name = name

    def get_name(self):
        return self._name

    def get_conn(self):
        return self._conn


def check_opt(opt, opts, check):
    for row in opts:
        if opt == row[0]:
            return check(row[1])
    return False


@logger('Server has started')
def main():
    opts = getopt.getopt(sys.argv[1:], 'a:p:')[0]
    if not (check_opt('-a', opts, is_ip) and check_opt('-p', opts, port_is_valid)):
        print('Usage: {} -p <port> -a <address>'.format(sys.argv[0]))
        sys.exit(BAD_OPTS)
    opts = dict(opts)
    addr = opts['-a']
    port = int(opts['-p'])

    jim = JIMServer(addr, port)
    jim.start()


if __name__ == '__main__':
    main()
