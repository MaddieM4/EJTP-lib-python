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

import ejtp.crypto
from ejtp.util.py2and3 import JSONBytesEncoder

class Identity(object):
    def __init__(self, name, encryptor, location, **kwargs):
        '''
        >>> ident = Identity("joe", ['rotate', 8], None)
        >>> ident.name
        'joe'
        '''
        self._contents = {
            'name': name,
            'encryptor': encryptor,
            'location': location,
        }
        self._contents.update(kwargs)
        self._encryptor = None

    def __getitem__(self, i):
        return self._contents[i]

    def __setitem__(self, i, v):
        self._contents[i] = v

    def __delitem__(self, i):
        del self._contents[i]

    # Encryptor shortcuts

    def encrypt(self, plaintext):
        return self.encryptor.encrypt(plaintext)

    def decrypt(self, ciphertext):
        return self.encryptor.decrypt(ciphertext)

    def sign(self, plaintext):
        return self.encryptor.sign(plaintext)

    def verify_signature(self, signature, plaintext):
        return self.encryptor.sig_verify(plaintext, signature)

    def public(self):
        '''
        Return a copy of this Identity with only the public component of
        its encryptor object.
        '''
        public_proto = self.encryptor.public()
        return Identity(self.name, public_proto, self.location)

    def is_public(self):
        return self.encryptor.is_public()

    def can_encrypt(self):
        return self.encryptor.can_encrypt()

    # Inner property and serialization stuff

    def serialize(self):
        '''
        Serialize Identity object to dict.
        '''
        self['encryptor'] = self.encryptor.proto()
        return self._contents

    def _get_name(self):
        return self['name']

    def _set_name(self, v):
        self['name'] = v

    name = property(_get_name, _set_name)

    def _get_location(self):
        return self['location']

    def _set_location(self, v):
        self['location'] = v

    location = property(_get_location, _set_location)

    def _get_encryptor(self):
        if not self._encryptor:
            self._encryptor = ejtp.crypto.make(self['encryptor'])
        return self._encryptor

    def _set_encryptor(self, new_encryptor):
        self._encryptor = ejtp.crypto.make(new_encryptor)
        self['encryptor'] = self.encryptor.proto()

    encryptor = property(_get_encryptor, _set_encryptor)

def deserialize(ident_dict):
    '''
    Deserialize a dict into an Identity.
    '''
    for req in ('name', 'location', 'encryptor'):
        if not req in ident_dict:
            raise ValueError("Missing ident property: %r" % req)

    name      = ident_dict['name']
    location  = ident_dict['location']
    encryptor = ident_dict['encryptor']

    cleaned = {}
    cleaned.update(ident_dict)
    del cleaned['name'], cleaned['location'], cleaned['encryptor']

    return Identity(name, encryptor, location, **cleaned)
