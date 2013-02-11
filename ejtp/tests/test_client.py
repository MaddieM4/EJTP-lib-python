import logging

from ejtp.util.compat import unittest, StringIO

from ejtp import client
from ejtp.client import Client
from ejtp.router import Router
from ejtp.util.py2and3 import RawData


class TestClient(unittest.TestCase):

    def setUp(self):
        self.stream = StringIO()
        handler = logging.StreamHandler(self.stream)
        client.logger.setLevel(logging.INFO)
        client.logger.addHandler(handler)

    def _assert(self, expected, value):
        self.assertEqual(expected, value.replace("u'", "'"))

    def test_encryptor_getter_and_setter(self):
        from ejtp.crypto.rotate import RotateEncryptor

        client = Client(None, None, make_jack=False)
        client.encryptor_set(["x", ["y", 8], "z"], ['rotate', 4])
        e = client.encryptor_get('["x",["y",8],"z"]')
        self.assertIsInstance(e, RotateEncryptor)

    def test_sign(self):
        client = Client(None, ['demo_interface'])
        client.encryptor_set(client.interface, ['rotate', 41])
        original = ['catamaran']
        signature = client.sign(original)
        self.assertEqual('RawData(3a0a0e3b3c39100e0f3d3a380b0c0d0807390f0f0c390e0e083d3a383a3a0b10393d0b090c3a0a0b)', repr(signature))

    def test_sig_verify(self):
        client = Client(None, ['demo_interface'])
        client.encryptor_set(client.interface, ['rotate',41])
        original = ['catamaran']
        self.assertTrue(client.sig_verify(original, client.interface, client.sign(original)))

    def test_clients_chat(self):
        router = Router()
        c1 = Client(router, ['udp', ['127.0.0.1', 555], 'c1'], make_jack=False)
        c2 = Client(router, ['udp', ['127.0.0.1', 555], 'c2'], make_jack=False)

        c1.encryptor_cache = c2.encryptor_cache # Let's only set this stuff once
        c1.encryptor_set(c1.interface, ['rotate',  3])
        c1.encryptor_set(c2.interface, ['rotate', -7])
        self.assertEqual(c1.router, c2.router)

        c1.write_json(c2.interface, "hello")
        c2.write_json(c1.interface, "goodbye")
        result = self.stream.getvalue().strip().split('\n')
        self._assert("Client ['udp', ['127.0.0.1', 555], 'c2'] recieved from ['udp', ['127.0.0.1', 555], 'c1']: RawData(2268656c6c6f22)", result[0])
        self._assert("Client ['udp', ['127.0.0.1', 555], 'c1'] recieved from ['udp', ['127.0.0.1', 555], 'c2']: RawData(22676f6f6462796522)", result[1])
