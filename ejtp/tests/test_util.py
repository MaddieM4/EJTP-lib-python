from ejtp.util.py2and3 import RawData, String
from ejtp.util import hasher
from ejtp.util.compat import json, unittest


class TestHasherMake(unittest.TestCase):

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


class TestHasherStrict(unittest.TestCase):

    def _assert(self, expected, value):
        value = hasher.strict(value)
        self.assertEqual(RawData(expected), RawData(value))

    def test_String_object(self):
        self._assert('"test"', String('test'))

    def test_RawData(self):
        self._assert('"test"', RawData('test'))

    def test_bool(self):
        self._assert('false', False)

    def test_none(self):
        self._assert('null', None)

    def test_string(self):
        self._assert('"test"', 'test')

    def test_int(self):
        self._assert('1', 1)

    def test_list(self):
        self._assert('["test1","test2"]', ['test1', 'test2'])

    def test_tuple(self):
        self._assert('["test1","test2"]', ('test1', 'test2'))

    def test_dict(self):
        self._assert('{"test1":1,"test2":2}', {'test1': 1, 'test2': 2})


class TestHasherStrictify(unittest.TestCase):

    def _assert(self, expected, value):
        value = hasher.strictify(json.dumps(value))
        self.assertEqual(RawData(expected), RawData(value))

    def test_bool(self):
        self._assert('false', False)

    def test_none(self):
        self._assert('null', None)

    def test_string(self):
        self._assert('"test"', 'test')

    def test_int(self):
        self._assert('1', 1)

    def test_list(self):
        self._assert('["test1","test2"]', ['test1', 'test2'])

    def test_tuple(self):
        self._assert('["test1","test2"]', ('test1', 'test2'))

    def test_dict(self):
        self._assert('{"test1":1,"test2":2}', {'test1': 1, 'test2': 2})


class TestHasherChecksum(unittest.TestCase):

    def test_calls(self):
        mock = lambda func, value: '%s_%s' % (func, value)
        try:
            self._strict = hasher.strict
            self._make = hasher.make
            hasher.strict = lambda x: mock('strict', x)
            hasher.make = lambda x: mock('make', x)
            self.assertEqual('make_strict_test', hasher.checksum('test'))
        finally:
            hasher.strict = self._strict
            hasher.make = self._make

    def test_string(self):
        expected = '5006d6f8302000e8b87fef5c50c071d6d97b4e88'
        value = hasher.checksum('test')
        self.assertEqual(RawData(expected), RawData(value))
