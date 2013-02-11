from __future__ import with_statement

import os
import imp
import sys

from ejtp.util.compat import json, unittest, StringIO

root = os.path.join(os.path.split(__file__)[0], '../..')

class IOMock(object):

    def __init__(self, input=None):
        self._stream = []
        self.input = input or []
        self.output = []

    def readline(self):
        _input = self.input.pop(0)
        self._stream.append('$ ' + _input)
        return _input

    def read(self):
        text = '\n'.join(self.input)
        return text

    def write(self, text):
        _output = text.strip().split('\n')
        self._stream.extend(_output)
        self.output.extend(_output)

    def __enter__(self):
        sys.stdin = sys.stdout = self

    def __exit__(self, type, value, traceback):
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__

    def get_lines(self):
        return [line for line in self._stream if line]

    def get_value(self):
        return '\n'.join(self.get_lines())

    def pipe(self):
        self.input = self.output
        self.output = []
        self._stream = []



class TestConsole(unittest.TestCase):

    def _import(self):
        with open(os.path.join(root, 'scripts', 'ejtp-console'), 'rb') as fp:
            return imp.load_module('console', fp, 'ejtp-console', ('.py', 'rb', imp.PY_SOURCE))

    def setUp(self):
        self.io = IOMock()
        self.console = self._import()
        self.inter = self.console.Interactive()

    def _assertCLI(self, expected):
        lines_expected = [line.strip() for line in expected.strip().split('\n')]
        self.io.input.extend([line[2:] for line in lines_expected if line.startswith('$')])

        with self.io:
            self.assertRaises(SystemExit, self.inter.repl)

        for pair in zip(lines_expected, self.io.get_lines()):
            if pair[0].startswith('$'):
                self.assertEqual(*pair)
            else:
                self.assertIn(*pair)

    def test_quit(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)

    def test_eval(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ eval
        $ 2 ** 10
        1024
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)

    def test_messages(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ send
        What interface do you want to send to?
        Available interfaces:
        $ mitzi@lackadaisy.com
        What message do you want to send?
        $ "one message"
        Enter a command
        $ messages
        All messages
        ------------
        mitzi@lackadaisy.com
        "one message"
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)

    def test_set_client(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ set client
        What interface do you want to use?
        Available interfaces:
        $ victor@lackadaisy.com
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)


class TestCrypto(unittest.TestCase):

    def _import(self):
        file_ = os.path.abspath(os.path.join(root, 'scripts', 'ejtp-crypto'))
        with open(file_, 'rb') as fp:
            return imp.load_module('crypto', fp, 'ejtp-crypto', ('.py', 'rb', imp.PY_SOURCE))

    def setUp(self):
        self.crypto = self._import()
        if not self.crypto:
            self.crypto = crypto
        self.io = IOMock()

    def test_encode_decode_id(self):
        argv = ['ejtp-crypto', 'encode', 'id', 'mitzi@lackadaisy.com']
        self.io.input.append('banana')
        with self.io:
            self.crypto.main(argv)

        argv = ['ejtp-crypto', 'decode', 'id', 'mitzi@lackadaisy.com']
        self.io.pipe()
        with self.io:
            self.crypto.main(argv)

        self.assertEqual('banana', self.io.get_value())

