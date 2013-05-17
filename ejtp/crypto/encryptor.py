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

from persei import String, RawDataDecorator, StringDecorator

from ejtp.util.hasher import strict
from Crypto.Hash import SHA256 as hashclass
import streql

class Encryptor(object):
    def encrypt(self, s):
        raise NotImplementedError("Encryptor must define 'encrypt'")

    def decrypt(self, s):
        raise NotImplementedError("Encryptor must define 'decrypt'")

    def public(self):
        # Returns a prototype for the public version of the key.
        # Assumes shared key = your key, overwrite for key types
        # where your public key and private key are different.
        return self.proto()

    def is_public(self):
        return self.proto() == self.public()

    def can_encrypt(self):
        '''
        Is this encryptor capable of encryption?

        By default, assumes true. Override where this is not guaranteed.
        '''
        return True

    @RawDataDecorator(strict=True)
    def hash_obj(self, plaintext):
        '''
        Produces a Crypto.Hash object.
        '''
        h = hashclass.new()
        h.update(plaintext.export())
        return h

    @RawDataDecorator(ret=True, strict=True)
    def hash(self, plaintext):
        '''
        Produces a binary SHA-256 hash.
        '''
        return self.hash_obj(plaintext.export()).digest()

    @RawDataDecorator(ret=True, strict=True)
    def sign(self, plaintext):
        '''
        Override in subclasses where you can't decrypt plaintext
        '''
        h = self.hash(plaintext)
        return self.decrypt(h)

    @RawDataDecorator(strict=True)
    def sig_verify(self, plaintext, signature):
        '''
        Verify a signature, by comparing it against a new signature
        of the same source data.
        '''
        return streql.equals(signature.export(), self.sign(plaintext).export())

    def flip(self):
        return Flip(self)

    def __str__(self):
        return strict(self.proto())

class Flip(Encryptor):
    def __init__(self, parent):
        self.encrypt = parent.decrypt
        self.decrypt = parent.encrypt

@StringDecorator()
def make(data):
    if isinstance(data, String):
        import json
        data = json.loads(data.export())
    if isinstance(data, Encryptor):
        return data
    t = data[0]
    args = data[1:]
    if t=="rotate":
        from . import rotate
        return rotate.RotateEncryptor(*args)
    elif t=="aes":
        from . import aes
        return aes.AESEncryptor(*args)
    elif t=="rsa":
        from . import rsa
        return rsa.RSA(*args)
    elif t=="ecc":
        from . import ecc
        return ecc.ECC(*args)
    else:
        raise TypeError("Unsupported encryption type: %r"%data)
