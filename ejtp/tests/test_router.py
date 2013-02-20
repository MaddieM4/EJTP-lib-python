from ejtp.util.compat import unittest
from ejtp.tests.tools import TestCaseWithLog
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


class TestRouterStream(TestCaseWithLog):

    def setUp(self):
        TestCaseWithLog.setUp(self)
        self.router = router.Router()
        self.listen(router.logger)

    def _test_message(self, expected, message='Jam and cookies', destination='["local",null,"example"]', format=None):
        data = ''.join([format, destination, '\x00', message])
        self.router.recv(data)
        self.assertInLog(expected)

    def test_recv_invalid_message(self):
        self.router.recv('qwerty')
        self.assertInLog("Router could not parse frame: 'qwerty'")

    def test_client_inexistent(self):
        self._test_message('Router could not deliver frame', format='r')

    def test_frame_with_no_destination(self):
        self._test_message('Frame recieved directly from', format='s')

    def test_frame_with_weird_type(self):
        self._test_message('Router could not parse frame: \'x["local",null,"example"]\\x00Jam and cookies\'', format='x')
