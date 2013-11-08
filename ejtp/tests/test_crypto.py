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

from Crypto.Hash import SHA256
from persei import RawData

from ejtp.util.compat import unittest

from ejtp.crypto import make
from ejtp.crypto.ecc import ECC
from ejtp.crypto.rsa import RSA

try:
    import pyecc
    has_ecc = True
except ImportError:
    print('WARNING: PyECC not found. Skipping ECC encryptor tests.')
    has_ecc = False


class TestEncryptor(unittest.TestCase):

    def setUp(self):
        self.re = make(['rotate', 38])
        self.plaintext = 'hello, world'

    def test_hash(self):
        self.assertEqual(self.re.hash('hello, world'),
            RawData((0x09,0xca,0x7e,0x4e,0xaa,0x6e,0x8a,0xe9,0xc7,0xd2,0x61,0x16,0x71,0x29,0x18,0x48,0x83,0x64,0x4d,0x07,0xdf,0xba,0x7c,0xbf,0xbc,0x4c,0x8a,0x2e,0x08,0x36,0x0d,0x5b))
        )
        self.assertEqual(self.re.hash('a'*300),
            RawData((0x98,0x35,0xfa,0x6b,0xf4,0xe2,0x0a,0x9b,0x9e,0xa8,0x12,0x50,0x63,0x02,0xe9,0x89,0x82,0x72,0x1a,0x6c,0xf8,0xd2,0xca,0xe6,0x7a,0xf5,0x71,0x29,0xbf,0x21,0xae,0x90))
        )

    def test_hash_obj(self):
        self.assertIsInstance(self.re.hash_obj('hello, world'), SHA256.SHA256Hash)

    def test_sign(self):
        sig = self.re.sign(self.plaintext)
        self.assertEqual(sig,
            RawData((0xe3,0xa4,0x58,0x28,0x84,0x48,0x64,0xc3,0xa1,0xac,0x3b,0xf0,0x4b,0x03,0xf2,0x22,0x5d,0x3e,0x27,0xe1,0xb9,0x94,0x56,0x99,0x96,0x26,0x64,0x08,0xe2,0x10,0xe7,0x35)))
        self.assertEqual(self.re.encrypt(sig),
            RawData((0x09,0xca,0x7e,0x4e,0xaa,0x6e,0x8a,0xe9,0xc7,0xd2,0x61,0x16,0x71,0x29,0x18,0x48,0x83,0x64,0x4d,0x07,0xdf,0xba,0x7c,0xbf,0xbc,0x4c,0x8a,0x2e,0x08,0x36,0x0d,0x5b)))
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

    def test_generate(self):
        myrsa = RSA(None, 1024)
        proto = myrsa.proto()
        self.assertEqual(len(proto), 2)
        self.assertEqual(proto[0], 'rsa')
        self.assertTrue(
            proto[1].startswith(
                RawData('-----BEGIN RSA PRIVATE KEY-----\n').export()
            )
        )

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


@unittest.skipUnless(has_ecc, 'PyECC is not installed.')
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
        ecc = make(['ecc', self.public_key, None, 'p184'])
        ecc.can_encrypt()

    def test_encrypt_decrypt(self):
        ecc = ECC(self.public_key, self.private_key, 'p184')
        encrypted = ecc.encrypt('test')
        self.assertNotEqual('test', encrypted.export())
        decrypted = ecc.decrypt(encrypted)
        self.assertEqual('test', decrypted.export())


@unittest.skipIf(has_ecc, 'PyECC is installed.')
class TestECCNotInstalled(unittest.TestCase):

    def test_ecc_should_raise(self):
        self.assertRaisesRegexp(TypeError, 'PyECC is not installed', ECC, None, None, None)
