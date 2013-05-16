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

from persei import RawDataDecorator

from ejtp.crypto import encryptor

class ECC(encryptor.Encryptor):
    def __init__(self, public, private, curve):
        try:
            from pyecc import ECC as _ECC
        except ImportError:
            raise TypeError('PyECC is not installed')

        self._ecc = _ECC(public=public or '', private=private, curve=curve)
        self._can_encrypt = bool(private)
        self.__curve = curve

    @RawDataDecorator(ret=True, strict=True)
    def encrypt(self, source):
        return self._ecc.encrypt(source.export())

    @RawDataDecorator(ret=True, strict=True)
    def decrypt(self, source):
        return self._ecc.decrypt(source.export())

    def can_encrypt(self):
        return self._can_encrypt

    def proto(self):
        return ['ecc', self.__curve]
