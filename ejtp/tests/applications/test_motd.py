from ejtp.util.compat import unittest

from ejtp.applications.motd import MOTDServer, MOTDClient

class TestMotd(unittest.TestCase):

    def setUp(self):
        from ejtp.router import Router
        router = Router()
        server_interface = ['local', None, 'motdserver']
        client_interface = ['local', None, 'motdclient']
        self.server = MOTDServer(router, server_interface, "", "Example message")
        self.client = MOTDClient(router, client_interface)
        self.client.encryptor_cache = self.server.encryptor_cache
        self.client.encryptor_set(server_interface, ['rotate', 143])
        self.client.encryptor_set(client_interface, ['rotate', 222])

    def test_response(self):
        def assert_response(msg, c):
            self.assertEqual(msg.jsoncontent['content'], 'Example message')
        self.client.request(self.server.interface, assert_response)
