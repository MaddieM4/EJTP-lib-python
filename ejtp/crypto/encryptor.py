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


from ejtp.util.hasher import strict
from ejtp.util.py2and3 import is_string
from Crypto.Hash import SHA256 as hashclass

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

    def hash_obj(self, plaintext):
        '''
        Produces a Crypto.Hash object.

        >>> re = make(['rotate', 38])
        >>> re.hash_obj('hello, world') #doctest: +ELLIPSIS
        <Crypto.Hash.SHA256.SHA256Hash instance at ...>
        '''
        h = hashclass.new()
        h.update(plaintext)
        return h

    def hash(self, plaintext):
        '''
        Produces a binary SHA-256 hash.

        >>> re = make(['rotate', 38])
        >>> re.hash('hello, world')
        '\\t\\xca~N\\xaan\\x8a\\xe9\\xc7\\xd2a\\x16q)\\x18H\\x83dM\\x07\\xdf\\xba|\\xbf\\xbcL\\x8a.\\x086\\r['
        >>> re.hash('a'*300)
        '\\x985\\xfak\\xf4\\xe2\\n\\x9b\\x9e\\xa8\\x12Pc\\x02\\xe9\\x89\\x82r\\x1al\\xf8\\xd2\\xca\\xe6z\\xf5q)\\xbf!\\xae\\x90'
        '''
        return self.hash_obj(plaintext).digest()

    def sign(self, plaintext):
        '''
        Override in subclasses where you can't decrypt plaintext

        >>> plaintext = 'hello, world'
        >>> re  = make(['rotate', 38])
        >>> sig = re.sign(plaintext)
        >>> sig
        '\\xe3\\xa4X(\\x84Hd\\xc3\\xa1\\xac;\\xf0K\\x03\\xf2"]>\\'\\xe1\\xb9\\x94V\\x99\\x96&d\\x08\\xe2\\x10\\xe75'
        >>> re.encrypt(sig)
        '\\t\\xca~N\\xaan\\x8a\\xe9\\xc7\\xd2a\\x16q)\\x18H\\x83dM\\x07\\xdf\\xba|\\xbf\\xbcL\\x8a.\\x086\\r['
        >>> re.encrypt(sig) == re.hash(plaintext)
        True
        '''
        h = self.hash(plaintext)
        return self.decrypt(h)

    def sig_verify(self, plaintext, signature):
        '''
        Verify a signature, by comparing it against a new signature
        of the same source data.

        >>> plaintext = 'hello, world'
        >>> re  = make(['rotate', 38])
        >>> sig = re.sign(plaintext)
        >>> re.sig_verify(plaintext, sig)
        True
        >>> re.sig_verify("other text", sig)
        False
        '''
        return signature == self.sign(plaintext)

    def flip(self):
        return Flip(self)

    def __str__(self):
        return strict(self.proto())

class Flip(Encryptor):
    def __init__(self, parent):
        self.encrypt = parent.decrypt
        self.decrypt = parent.encrypt

def make(data):
    if is_string(data):
        import json
        data = json.loads(data)
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
    else:
        raise TypeError("Unsupported encryption type: %r"%data)
