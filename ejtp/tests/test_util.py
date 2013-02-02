import unittest

from ejtp.util.py2and3 import RawData
from ejtp.util import hasher


class TestHasher(unittest.TestCase):

    text = 'Sample string'
    expected_hash = 'e9a47e5417686cf0ac5c8ad9ee90ba2c1d08cc14'

    def _assert(self, expected, value):
        self.assertEqual(RawData(expected), RawData(value))

    def test_make(self):
        self._assert(self.expected_hash, hasher.make(self.text))

    def test_make6(self):
        self._assert(self.expected_hash[:6], hasher.make6(self.text))

    def test_maken(self):
        self._assert(self.expected_hash[:3], hasher.maken(self.text, 3))
