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

import sys
from Crypto.Hash import SHA256
from ejtp.util.compat import unittest, is_py3k

from ejtp.util.py2and3 import RawData
from ejtp.crypto import make
from ejtp.crypto.ecc import ECC
from ejtp.crypto.rsa import RSA


skipPy3k = unittest.skipIf(is_py3k, 'Python 3.x does not have PyECC dependency.')
onlyPy3k = unittest.skipUnless(is_py3k, 'Python 2.x have PyECC dependency.')


class TestEncryptor(unittest.TestCase):

    def setUp(self):
        self.re = make(['rotate', 38])
        self.plaintext = 'hello, world'

    def test_hash(self):
        self.assertEqual(self.re.hash('hello, world'),
            RawData('\t\xca~N\xaan\x8a\xe9\xc7\xd2a\x16q)\x18H\x83dM\x07\xdf\xba|\xbf\xbcL\x8a.\x086\r['))
        self.assertEqual(self.re.hash('a'*300),
            RawData('\x985\xfak\xf4\xe2\n\x9b\x9e\xa8\x12Pc\x02\xe9\x89\x82r\x1al\xf8\xd2\xca\xe6z\xf5q)\xbf!\xae\x90'))

    def test_hash_obj(self):
        self.assertIsInstance(self.re.hash_obj('hello, world'), SHA256.SHA256Hash)

    def test_sign(self):
        sig = self.re.sign(self.plaintext)
        self.assertEqual(sig,
            RawData('\xe3\xa4X(\x84Hd\xc3\xa1\xac;\xf0K\x03\xf2"]>\'\xe1\xb9\x94V\x99\x96&d\x08\xe2\x10\xe75'))
        self.assertEqual(self.re.encrypt(sig),
            RawData('\t\xca~N\xaan\x8a\xe9\xc7\xd2a\x16q)\x18H\x83dM\x07\xdf\xba|\xbf\xbcL\x8a.\x086\r['))
        self.assertEqual(self.re.encrypt(sig), self.re.hash(self.plaintext))

    def test_sig_verify(self):
        sig = self.re.sign(self.plaintext)
        self.assertTrue(self.re.sig_verify(self.plaintext, sig))
        self.assertFalse(self.re.sig_verify("other text", sig))


class TestRSA(unittest.TestCase):

    def setUp(self):
        self.plaintext = 'hello world'
        self.private_key = '-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQCnA7oUrAe0JgMZfPzrdmaUjwkomYVXSmamemPaINybgDIIHDDr\nizwq8agHIvc/kwQ6ZZP9XQA/YbKq9rqaCD5yvwIyet/MiFz8b1zh1tSte4uDV9vU\nuTaF4y+1TmZVtZbfmC4E2ic/i72mJKy02FExvm+oAObFSraOfLiShUubSQIDAQAB\nAn8aGHr6v+Z0P3w8f0sFf3qHu9GyhkpPWVCwsm7npjrSETXADqeWJitAioG2m8AG\nLvJ6LWTyMZXYUWuZSvPdHWykQD/VMn7F5jIy5hjzYON/a7mBYPw0NFdUc4VTR4dU\nzuR9T0MkyIV9w4Rl3AU9SfpRneAtutoC4gqROrFLcWiBAkEAurSBELVUcvWTelFa\n8WsY474/j6DiZ3/jrDirblhqnRzZkIa9ETSzGNgmIRMtgabdkAgdoqDpJkwGzYAi\n+u3yBQJBAOUAW1tEQlwAYfMmFwzXLDZg7+t9nefTNr5SEY3KAoo+hLxxLeSwyp+k\ndzQfS8ITPS0o2bFHhD2uDFpbe3kRM3UCQB8kxPK4jKGwfS1GLNlgeAJlVczrlViW\naK/ttArwDLiwe0o0b41TMRzP0Wxq+ohKAWNpNyhNlxagT/IvkaYx0tECQQCRtoFq\n+GsVKXUqB3GhTQUn8NSYzox8Z4ws3AGpbAHjv1YspgOiwc+cd0UWWFeXPTCvHJAw\nWqZNrQLVN+LALW7FAkEAgkFG3700qy9L4kVdBYiGKyTgUGGLVKjegShyYY9jQBLO\nHk+tnhFsjc/wBaHlNAzScTJjjdJnNbGRtQtgtl86wA==\n-----END RSA PRIVATE KEY-----'
        self.public_key = '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnA7oUrAe0JgMZfPzrdmaUjwko\nmYVXSmamemPaINybgDIIHDDrizwq8agHIvc/kwQ6ZZP9XQA/YbKq9rqaCD5yvwIy\net/MiFz8b1zh1tSte4uDV9vUuTaF4y+1TmZVtZbfmC4E2ic/i72mJKy02FExvm+o\nAObFSraOfLiShUubSQIDAQAB\n-----END PUBLIC KEY-----'

    def test_sig_verify(self):
        myrsa = RSA(self.private_key)
        self.assertTrue(myrsa.sig_verify(self.plaintext, myrsa.sign(self.plaintext)))
        self.assertFalse(myrsa.sig_verify(self.plaintext, myrsa.sign('other text')))

    def test_sig_verify_with_public_key(self):
        myrsa = RSA(self.private_key)
        public = RSA(self.public_key)
        self.assertTrue(public.sig_verify(self.plaintext, myrsa.sign(self.plaintext)))
        self.assertFalse(public.sig_verify(self.plaintext, myrsa.sign('other text')))

    def test_sign_with_public_key(self):
        public = RSA(self.public_key)
        self.assertRaisesRegexp(TypeError,
            'RSA encryptor cannot sign without private key',
            public.sign, self.plaintext)

    def test_can_encrypt(self):
        myrsa = RSA(self.private_key)
        self.assertTrue(myrsa.can_encrypt())
        self.assertFalse(make(myrsa.public()).can_encrypt())


class TestECC(unittest.TestCase):

    private_key = '!!![t{l5N^uZd=Bg(P#N|PH#IN8I0,Jq/PvdVNi^PxR,(5~p-o[^hPE#40.<|'
    public_key = '#&M=6cSQ}m6C(hUz-7j@E=>oS#TL3F[F[a[q9S;RhMh+F#gP|Q6R}lhT_e7b'

    def test_can_encrypt(self):
        ecc = ECC(self.public_key, self.private_key, 'p184')
        self.assertTrue(ecc.can_encrypt())

    def test_cannot_encrypt(self):
        ecc = ECC(self.public_key, None, 'p184')
        self.assertFalse(ecc.can_encrypt())

    def test_make(self):
        from ejtp.crypto import make
        ecc = make(['ecc', self.public_key, None, 'p184'])
        ecc.can_encrypt()

    def test_encrypt_decrypt(self):
        ecc = ECC(self.public_key, self.private_key, 'p184')
        encrypted = ecc.encrypt('test')
        self.assertNotEqual('test', encrypted.export())
        decrypted = ecc.decrypt(encrypted)
        self.assertEqual('test', decrypted.export())


class TestECCPy3K(unittest.TestCase):

    def test_should_fail(self):
        self.assertRaises(TypeError, ECC, None, None, 'p184')


TestECC = skipPy3k(TestECC)
TestECCPy3K = onlyPy3k(TestECCPy3K)
