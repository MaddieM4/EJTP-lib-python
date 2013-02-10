from ejtp.util.compat import unittest

from ejtp.address import str_address, py_address
from ejtp.util.py2and3 import String

class TestPyAddress(unittest.TestCase):

    def _assert(self, expected, value):
        self.assertEqual(expected, py_address(value))

    def test_with_string(self):
        self._assert([0, 9], '[0,9]')

    def test_with_list(self):
        self._assert([0, 9], [0, 9])


class TestStrAddress(unittest.TestCase):

    def _assert(self, expected, value):
        self.assertEqual(expected, str_address(value))

    def test_with_string(self):
        self._assert(String('[0,9]'), '[0,9]')

    def test_with_list(self):
        self._assert(String('[0,9]'), [0, 9])
