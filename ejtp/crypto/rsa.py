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


import thread
import stream

from   Crypto.PublicKey import RSA as rsalib
from   Crypto.Cipher import PKCS1_OAEP as Cipher
from   Crypto.Signature import PKCS1_PSS as Signer
import Crypto.Util.number
from   Crypto.Util.number import ceil_div

class RSA(stream.StreamEncryptor):
    def __init__(self, keystr, keybits=1024):
        '''
        keystr  - The key contents as PEM data, or None (if you want to generate a new key)
        keybits - Only used if keystr is None. Default 1024.

        Testing based on signatures:

        >>> myrsa = RSA(SAMPLE_KEY_PRIVATE)
        >>> plaintext = 'hello world'
        >>> myrsa.sig_verify(plaintext, myrsa.sign(plaintext))
        True
        >>> myrsa.sig_verify(plaintext, myrsa.sign('other text'))
        False

        Let's make sure this also works with public keys:

        >>> public = RSA(SAMPLE_KEY_PUBLIC) # Public component of SAMPLE_KEY_PRIVATE
        >>> public.sig_verify(plaintext, myrsa.sign(plaintext))
        True
        >>> public.sig_verify(plaintext, myrsa.sign('other text'))
        False

        But not everyone should be able to sign with it.
        >>> public.sign(plaintext)
        Traceback (most recent call last):
        TypeError: No private key

        '''
        self.keystr = keystr
        if keystr == None:
            stream.StreamEncryptor.__init__(self, None)
            self.generate(keybits)
        else:
            stream.StreamEncryptor.__init__(self, rsalib.importKey(keystr))

    # Cryptographic properties

    @property
    def keysize(self):
        modBits = Crypto.Util.number.size(self.cipher._key.n)
        return ceil_div(modBits,8)

    @property
    def hashsize(self):
        return self.cipher._hashObj.digest_size

    @property
    def input_blocksize(self):
        # Size to split strings into while encrypting.
        k = self.keysize
        hLen = self.hashsize
        return k - (2*hLen) - 2

    @property
    def output_blocksize(self):
        # Size to split strings into while decrypting.
        return self.keysize

    def derive(self, key):
        '''
        Return (key, cipher, signer)
        '''
        return key, Cipher.new(key), Signer.new(key)

    # Asynchronous key generation

    def generate(self, bits=1024):
        thread.start_new_thread(self._generate, (bits,))

    def _generate(self, bits):
        self.set_key(rsalib.generate(bits))

    # Protocol data

    def proto(self):
        return ['rsa', self.key.exportKey()]

    def public(self):
        key = self.key.publickey()
        return ['rsa', key.exportKey()]

SAMPLE_KEY_PRIVATE = '-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQCnA7oUrAe0JgMZfPzrdmaUjwkomYVXSmamemPaINybgDIIHDDr\nizwq8agHIvc/kwQ6ZZP9XQA/YbKq9rqaCD5yvwIyet/MiFz8b1zh1tSte4uDV9vU\nuTaF4y+1TmZVtZbfmC4E2ic/i72mJKy02FExvm+oAObFSraOfLiShUubSQIDAQAB\nAn8aGHr6v+Z0P3w8f0sFf3qHu9GyhkpPWVCwsm7npjrSETXADqeWJitAioG2m8AG\nLvJ6LWTyMZXYUWuZSvPdHWykQD/VMn7F5jIy5hjzYON/a7mBYPw0NFdUc4VTR4dU\nzuR9T0MkyIV9w4Rl3AU9SfpRneAtutoC4gqROrFLcWiBAkEAurSBELVUcvWTelFa\n8WsY474/j6DiZ3/jrDirblhqnRzZkIa9ETSzGNgmIRMtgabdkAgdoqDpJkwGzYAi\n+u3yBQJBAOUAW1tEQlwAYfMmFwzXLDZg7+t9nefTNr5SEY3KAoo+hLxxLeSwyp+k\ndzQfS8ITPS0o2bFHhD2uDFpbe3kRM3UCQB8kxPK4jKGwfS1GLNlgeAJlVczrlViW\naK/ttArwDLiwe0o0b41TMRzP0Wxq+ohKAWNpNyhNlxagT/IvkaYx0tECQQCRtoFq\n+GsVKXUqB3GhTQUn8NSYzox8Z4ws3AGpbAHjv1YspgOiwc+cd0UWWFeXPTCvHJAw\nWqZNrQLVN+LALW7FAkEAgkFG3700qy9L4kVdBYiGKyTgUGGLVKjegShyYY9jQBLO\nHk+tnhFsjc/wBaHlNAzScTJjjdJnNbGRtQtgtl86wA==\n-----END RSA PRIVATE KEY-----'
SAMPLE_KEY_PUBLIC = '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnA7oUrAe0JgMZfPzrdmaUjwko\nmYVXSmamemPaINybgDIIHDDrizwq8agHIvc/kwQ6ZZP9XQA/YbKq9rqaCD5yvwIy\net/MiFz8b1zh1tSte4uDV9vUuTaF4y+1TmZVtZbfmC4E2ic/i72mJKy02FExvm+o\nAObFSraOfLiShUubSQIDAQAB\n-----END PUBLIC KEY-----'
