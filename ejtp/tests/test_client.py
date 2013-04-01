'''
This file is part of the Python EJTP library.

The Python EJTP library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Python EJTP library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Python EJTP library.  If not, see 
<http://www.gnu.org/licenses/>.
'''

import logging

from ejtp.tests.tools import TestCaseWithLog

from ejtp.client import Client, logger
from ejtp.router import Router


class TestClient(TestCaseWithLog):

    def setUp(self):
        TestCaseWithLog.setUp(self)
        self.listen(logger)

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
        self.assertEqual('RawData((0x3a,0xa,0xe,0x3b,0x3c,0x39,0x10,0xe,0xf,0x3d,0x3a,0x38,0xb,0xc,0xd,0x8,0x7,0x39,0xf,0xf,0xc,0x39,0xe,0xe,0x8,0x3d,0x3a,0x38,0x3a,0x3a,0xb,0x10,0x39,0x3d,0xb,0x9,0xc,0x3a,0xa,0xb))', repr(signature))

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
        self.assertInLog("Client ['udp', ['127.0.0.1', 555], 'c2'] recieved from ['udp', ['127.0.0.1', 555], 'c1']: JSONFrame: RawData((0x6a,0x0,0x22,0x68,0x65,0x6c,0x6c,0x6f,0x22))")
        self.assertInLog("Client ['udp', ['127.0.0.1', 555], 'c1'] recieved from ['udp', ['127.0.0.1', 555], 'c2']: JSONFrame: RawData((0x6a,0x0,0x22,0x67,0x6f,0x6f,0x64,0x62,0x79,0x65,0x22))")
