from __future__ import with_statement

import os
import imp
import sys

from ejtp.util.compat import json, unittest, StringIO

root = os.path.join(os.path.split(__file__)[0], '../..')

class IOMock(object):

    def __init__(self, input=None, output=None):
        self._stream = []
        self.input = input or []
        self.output = output or []

    def readline(self):
        _input = self.input.pop(0)
        self._stream.append(_input)
        return _input.lstrip('$ ')

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
        self.io.input.extend([line for line in lines_expected if line.startswith('$')])

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
