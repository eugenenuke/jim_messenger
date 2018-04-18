#!/usr/bin/env python3

from unittest.mock import Mock
import unittest
import argparse
import time
import json

from jimm import *
import server
import client


class TestIsIpFunction(unittest.TestCase):
    def test_no_dots(self):
        # self.aspsertFalse(is_ip('just a string'))
        with self.assertRaises(argparse.ArgumentTypeError):
            is_ip('just a string')

    def test_invalid_ndots(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            is_ip('127.1')
            is_ip('192.168.100')
            is_ip('..')
            is_ip('....')

    def test_invalid_octet(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            is_ip('192.168.0.256')
            is_ip('256.168.0.2')
            is_ip('192.256.0.100')
            is_ip('192.168.256.0')
            is_ip('1000.1000.1000.1000')
            is_ip('-1.-1.-1.-1')

    def test_correct_ip(self):
        self.assertEqual(is_ip('192.168.0.100'), '192.168.0.100')

    def test_invalid_type(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            is_ip(65535)


class TestPortIsNumFunction(unittest.TestCase):
    def test_string(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            port_is_valid('str')

    def test_mixed(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            port_is_valid('str123')
            port_is_valid('str.123')

    def test_valid_num(self):
        self.assertTrue(port_is_valid('123'))
        self.assertTrue(port_is_valid('65535'))

    def test_invalid_num(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            port_is_valid('0')
            port_is_valid('65536')

    def test_invalid_type(self):
        with self.assertRaises(AttributeError):
            port_is_valid(65535)


class TestJIMUser(unittest.TestCase):
    def test_creation(self):
        name = 'name'
        test_user = server.JIMUser(name, None)
        self.assertEqual(test_user.get_name(), name)


class TestJIMServer(unittest.TestCase):
    def setUp(self):
        self.test_srv = server.JIMServer('127.0.0.1', '7777')
    
    def test_action_presence(self):
        user = 'TestUser'
        request = {
                'action': 'presence',
                'time': int(time.time()),
                'type': 'status',
                'user': {
                    'account_name': user,
                    'status': 'I\'m here!'
                    }
                }
        self.assertFalse(self.test_srv.is_user_registered(user))
        res = self.test_srv.action_presence(request, None)[0]
        self.assertEqual(200, res)
        self.assertTrue(self.test_srv.is_user_registered(user))

        res = self.test_srv.action_presence(request, None)[0]
        self.assertEqual(409, res)
        res = self.test_srv.action_presence(request, None)[0]
        self.assertEqual(409, res)

        user = 'TestUser2'
        request['user']['account_name'] = user
        res = self.test_srv.action_presence(request, None)[0]
        self.assertEqual(200, res)
        self.assertTrue(self.test_srv.is_user_registered(user))

        res = self.test_srv.action_presence(request, None)[0]
        self.assertEqual(409, res)


class TestJIMClient(unittest.TestCase):
    def test_client(self):
        pass

    def setUp(self):
        # self.test_clnt = client.JIMClient('127.0.0.1', '7777')
        pass


if __name__ == '__main__':
    unittest.main()
