import logging

from ejtp.util.compat import unittest, StringIO

from ejtp.router import Router
from ejtp.applications.ejforward.client import ForwardClient, logger as client_logger
from ejtp.applications.ejforward.server import ForwardServer, logger as server_logger
from ejtp.util.hasher import strict
from ejtp.util.py2and3 import String

class TestClient(unittest.TestCase):

    def setUp(self):

        _demo_client_addr = ['local', None, 'client']
        _demo_server_addr = ['local', None, 'server']

        router = Router()
        self.client = ForwardClient(router, _demo_client_addr, _demo_server_addr)
        self.server = ForwardServer(router, _demo_server_addr)
        self.client.encryptor_set(_demo_client_addr, ['rotate', 5])
        self.client.encryptor_set(_demo_server_addr, ['rotate', 3])
        self.server.encryptor_cache = self.client.encryptor_cache
        self.server.setup_client(self.client.interface)

        self.stream = StringIO()
        handler = logging.StreamHandler(self.stream)
        formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
        handler.setFormatter(formatter)
        client_logger.setLevel(logging.INFO)
        client_logger.addHandler(handler)
        server_logger.setLevel(logging.INFO)
        server_logger.addHandler(handler)

    def _assertInStream(self, value):
        self.assertIn(value, self.stream.getvalue())

    def _assertStatus(self, expected):
        def on_status(client):
            status = strict(client.status).export()
            self.assertEqual(expected, status)

        self.client.get_status(on_status)

    def test_get_status(self):
        self._assertStatus('{"hashes":[],"total_count":1000,"total_space":32768,"type":"ejforward-notify","used_count":0,"used_space":0}')

    def test_server_store_message_and_retrieve(self):
        mhash = self.server.store_message(self.client.interface, "fakey message")
        messages = self.server.client(self.client.interface)['messages']
        self.assertEqual({String('4fc5bbbfefe38b84b935fee015c192e397b6eac3'): 'fakey message'}, messages)

        self._assertStatus('{"hashes":["4fc5bbbfefe38b84b935fee015c192e397b6eac3"],"total_count":1000,"total_space":32768,"type":"ejforward-notify","used_count":1,"used_space":13}')
        self.client.retrieve(hashes=[mhash])
        self._assertInStream('WARNING:ejtp.applications.ejforward.client: Invalid frame, discarding')

        messages = self.server.client(self.client.interface)['messages']
        self.assertEqual({}, messages)

        self._assertStatus('{"hashes":[],"total_count":1000,"total_space":32768,"type":"ejforward-notify","used_count":0,"used_space":0}')

    def test_upload(self):
        self.client.upload("farfagnugen", {})
        self._assertInStream("WARNING:ejtp.applications.ejforward.server: Unknown message type")
