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


try:
    import thread
except ImportError: # in python3.x it's renamed to _thread
    import _thread as thread
from persei import RawDataDecorator

from ejtp.crypto import encryptor

from   Crypto.PublicKey import RSA as rsalib
from   Crypto.Cipher import PKCS1_OAEP as Cipher
from   Crypto.Signature import PKCS1_PSS as Signer
import Crypto.Util.number
from   Crypto.Util.number import ceil_div

class RSA(encryptor.Encryptor):
    @RawDataDecorator()
    def __init__(self, keystr, bits=None):
        self.keystr = keystr
        self._key = None
        self.genlock = thread.allocate()
        if keystr == None:
            self.generate(bits=int(bits) or 1024)
        else:
            self.set_key(rsalib.importKey(keystr.export()))

    @RawDataDecorator(ret=True, strict=True)
    def encrypt(self, value):
        # Process in blocks
        length = len(value)
        split  = self.input_blocksize
        if length > split:
            return self.encrypt(value[:split].export()) + self.encrypt(value[split:].export())
        else:
            return self.cipher.encrypt(value.export())

    @RawDataDecorator(ret=True, strict=True)
    def decrypt(self, value):
        length = len(value)
        split  = self.output_blocksize
        if length > split:
            return self.decrypt(value[:split].export()) + self.decrypt(value[split:].export())
        elif length == split:
            return self.cipher.decrypt(value.export())
        else:
            raise ValueError("Wrong size for ciphertext, expected %d and got %d" % (split, length))

    @RawDataDecorator(ret=True, strict=True)
    def sign(self, plaintext):
        '''
        Override version using PKCS1_PSS signing to sign (and randomly salt) plaintext.
        '''
        try:
            return self.signer.sign(self.hash_obj(plaintext))
        except TypeError:
            # Raise consistent error description, regardless of PyCrypto version
            raise TypeError("RSA encryptor cannot sign without private key")
    
    @RawDataDecorator(strict=True)
    def sig_verify(self, plaintext, signature):
        '''
        Override version using PKCS1_PSS signing to verify a signature.
        '''
        return self.signer.verify(self.hash_obj(plaintext), signature.export())

    # Locking properties

    @property
    def key(self):
        with self.genlock:
            return self._key

    @property
    def cipher(self):
        with self.genlock:
            return self._cipher

    @property
    def signer(self):
        with self.genlock:
            return self._signer

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

    def set_key(self, key):
        self._key = key
        self._cipher = Cipher.new(self._key)
        self._signer = Signer.new(self._key)

    def generate(self, bits=1024):
        self.genlock.acquire()
        thread.start_new_thread(self._generate, (bits,))

    def _generate(self, bits):
        try:
            self.set_key(rsalib.generate(bits))
        finally:
            self.genlock.release()

    def proto(self):
        key = self.key
        return ['rsa', key.exportKey()]

    def public(self):
        key = self.key.publickey()
        return ['rsa', key.exportKey()]

    def can_encrypt(self):
        return self.key.has_private()
