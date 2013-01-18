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

class Identity(object):
    def __init__(self, name, encryptor, location):
        '''
        >>> ident = Identity("joe", ['rotate', 8], None)
        >>> ident.name
        'joe'
        >>> e =  ident.encryptor
        >>> e # doctest: +ELLIPSIS
        <ejtp.crypto.rotate.RotateEncryptor object at ...>
        >>> e == ident.encryptor # Make sure this is cached
        True
        >>> plaintext = "example"
        >>> sig = ident.sign(plaintext)
        >>> sig
        'H\\xd0P\\xd8\\x90V\\xc4wX9\\x82\\xa7\\x04\\xbd\\xa3Pw:\\xbaO\\x02\\x808\\x8d\\xa1\\xe0\\xc4\\xa4\\xc8\\xeeLT'
        >>> ident.verify_signature(sig, plaintext)
        True
        '''
        self._name = name
        self._encryptor_proto = encryptor
        self._encryptor = None
        self._location = location

    def sign(self, plaintext):
        return self.encryptor.sign(plaintext)

    def verify_signature(self, signature, plaintext):
        return self.encryptor.sig_verify(plaintext, signature)

    def public(self):
        '''
        Return a copy of this Identity with only the public component of
        its encryptor object.

        >>> from ejtp import testing
        >>> ident = testing.identity()
        >>> "PRIVATE" in ident.encryptor.proto()[1]
        True
        >>> "PUBLIC" in ident.encryptor.proto()[1]
        False
        >>> "PRIVATE" in ident.public().encryptor.proto()[1]
        False
        >>> "PUBLIC" in ident.public().encryptor.proto()[1]
        True
        '''
        public_proto = self.encryptor.public()
        return Identity(self.name, public_proto, self.location)

    @property
    def name(self):
        return self._name

    @property
    def encryptor(self):
        if not self._encryptor:
            self._encryptor = ejtp.crypto.make(self._encryptor_proto)
        return self._encryptor

    @encryptor.setter
    def encryptor(self, new_encryptor):
        self._encryptor = ejtp.crypto.make(new_encryptor)
        self._encryptor_proto = self.encryptor.proto()

    @property
    def location(self):
        if self._location:
            return self._location
        else:
            raise AttributeError("Identity location not set")

    @location.setter
    def location(self, value):
        self._location = value
