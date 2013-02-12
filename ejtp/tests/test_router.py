import logging

from ejtp.util.compat import unittest, StringIO
from ejtp import router

class TestRouter(unittest.TestCase):

    def setUp(self):
        self.router = router.Router()

    def test_jack_already_loaded(self):
        from ejtp.jacks import Jack
        class DummyJack(Jack):
            def run(self, *args):
                pass

        jack = DummyJack(self.router, (1, 2, 3))
        self.assertRaisesRegexp(ValueError,
            'jack already loaded', self.router._loadjack, jack)

    def test_client_already_loaded(self):
        from ejtp.client import Client
        client = Client(None, (4, 5, 6), make_jack = False)
        self.router._loadclient(client)
        self.assertRaisesRegexp(ValueError,
            'client already loaded', self.router._loadclient, client)


class TestRouterLog(unittest.TestCase):

    def setUp(self):
        self.router = router.Router()
        self.stream = StringIO()
        handler = logging.StreamHandler(self.stream)
        router.logger.setLevel(logging.INFO)
        router.logger.addHandler(handler)

    def test_recv_invalid_message(self):
        self.router.recv('qwerty')
        self.assertIn("Router could not parse frame: 'qwerty'", self.stream.getvalue())
