from ejtp.util.compat import unittest

class TestCaseWithLog(unittest.TestCase):

    def setUp(self):
        from ejtp.util.compat import StringIO
        self._stream = StringIO()

    def listen(self, logger):
        import logging
        handler = logging.StreamHandler(self._stream)
        formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    def assertInLog(self, expected):
        value = self._stream.getvalue()
        try:
            self.assertIn(expected, value)
        except AssertionError:
            self.assertIn(expected, value.replace("u'", "'"))
