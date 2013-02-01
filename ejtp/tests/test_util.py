import unittest

from ejtp.util import hasher

class TestHasher(unittest.TestCase):

    expected_sha1 = 'e9a47e5417686cf0ac5c8ad9ee90ba2c1d08cc14'

    def test_make(self):
        self.assertEqual(self.expected_sha1, hasher.make('Sample string').export())

    def test_make6(self):
        self.assertEqual(self.expected_sha1[:6], hasher.make6('Sample string').export())

    def test_maken(self):
        self.assertEqual(self.expected_sha1[:3], hasher.maken('Sample string', 3).export())
