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
from Crypto.Cipher import PKCS1_OAEP as Cipher
from Crypto.Signature import PKCS1_PSS as Signer

import encryptor

class StreamEncryptor(encryptor.Encryptor):
    '''
    Intermediate subclass for PKCS1 padding and signing.

    Provides support for generating keys asynchronously and block encryption.
    '''

    def __init__(self, key_obj=None):
        self._key_wait = thread.allocate()
        self._key_wait.acquire()
        self.set_key(key_obj)

    def set_key(self, key_obj):
        if key_obj:
            try:
                self._key    = key_obj
                self._cipher = Cipher.new(self._key)
                self._signer = Signer.new(self._key)
            finally:
                if self._key_wait.locked():
                    self._key_wait.release()
        else:
            self._key    = None
            self._cipher = None
            self._signer = None

    # Locking properties

    @property
    def key(self):
        with self._key_wait:
            return self._key

    @property
    def cipher(self):
        with self._key_wait:
            return self._cipher

    @property
    def signer(self):
        with self._key_wait:
            return self._signer

    # Signing stuff

    def sign(self, plaintext):
        '''
        Override version using PKCS1_PSS signing to sign (and randomly salt) plaintext.
        '''
        return self.signer.sign(self.hash_obj(plaintext))

    def sig_verify(self, plaintext, signature):
        '''
        Override version using PKCS1_PSS signing to verify a signature.
        '''
        return self.signer.verify(self.hash_obj(plaintext), signature)

    # Cryptographic properties - necessary for chunking

    @property
    def input_blocksize(self):
        raise NotImplementedError("Subclass of StreamEncryptor should provide input_blocksize")

    @property
    def output_blocksize(self):
        raise NotImplementedError("Subclass of StreamEncryptor should provide output_blocksize")

    # Core functions

    def encrypt(self, value):
        # Process in blocks
        value  = str(value)
        length = len(value)
        split  = self.input_blocksize
        if length > split:
            return self.encrypt(value[:split]) + self.encrypt(value[split:])
        else:
            return self.cipher.encrypt(value)

    def decrypt(self, value):
        value  = str(value)
        length = len(value)
        split  = self.output_blocksize
        if length > split:
            return self.decrypt(value[:split]) + self.decrypt(value[split:])
        elif length == split:
            return self.cipher.decrypt(value)
        else:
            raise ValueError("Wrong size for ciphertext, expected %d and got %d" % (split, length))
