from __future__ import with_statement
from ejtp.util.compat import unittest

from ejtp.util.py2and3 import RawData
from ejtp.jacks.stream import Connection

class TestJackStream(unittest.TestCase):

    def setUp(self):
        self.connection = Connection()
        self.plaintext = "The pursuit of \x00 happiness"
        self.wrapped = self.connection.wrap(self.plaintext)

    def test_receive(self):
        self.connection.inject(self.wrapped)
        self.assertEqual(RawData(self.plaintext), self.connection.recv())

    def test_receive_partial(self):
        self.connection.inject(self.wrapped[:5])
        self.assertIsNone(self.connection.recv())

        self.connection.inject(self.wrapped[5:])
        self.assertEqual(RawData(self.plaintext), self.connection.recv())

