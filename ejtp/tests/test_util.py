import unittest

from ejtp.util import hasher

class TestHasher(unittest.TestCase):

    def test_make(self):
        expected = 'e9a47e5417686cf0ac5c8ad9ee90ba2c1d08cc14'
        self.assertEquals(expected, hasher.make('Sample string').export())