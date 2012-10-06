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


from stream import StreamEncryptor

from Crypto.Cipher import AES
from Crypto import Random

class AESEncryptor(StreamEncryptor):
    def __init__(self, keystr):
        '''
        keystr - string with a length that is a multiple of 16

        >>> keystr = make_keystr("kitty")
        >>> len(keystr)
        32
        >>> aes = AESEncryptor(keystr)
        '''
        StreamEncryptor.__init__(self, keystr)

    # Cryptographic properties

    @property
    def input_blocksize(self):
        return AES.block_size

    @property
    def output_blocksize(self):
        return AES.block_size

    def derive(self, key):
        iv = Random.new().read(AES.block_size)
        return key, AES.new(key, AES.MODE_CFB, iv), None

    # Core functions

    def encrypt(self, value):
        self.derive(self.key)
        return StreamEncryptor.encrypt(self, value)

    def decrypt(self, value):
        self.derive(self.key)
        return StreamEncryptor.decrypt(self, value)

    # Protocol data

    def proto(self):
        return ['aes', self.keystr]

def make_keystr(password):
    '''
    Returns 32 bit digest from SHA256-ing the password.

    Password may be any length, longer = more entropy = better.
    '''
    from Crypto.Hash import SHA256
    return SHA256.new(password).digest()
