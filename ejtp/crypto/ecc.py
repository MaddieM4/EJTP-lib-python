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
    from pyecc import ECC as _ECC
except ImportError:
    class _ECC(object):

        def __init__(self, *args, **kwargs):
            # TODO: add a warning here
            pass

        def encrypt(self, source):
            return source

        def decrypt(self, source):
            return source


from ejtp.crypto import encryptor
from ejtp.util.py2and3 import RawDataDecorator

class ECC(encryptor.Encryptor):
    def __init__(self, public, private, curve):
        kwargs = {}

        self._ecc = _ECC(public=public, private=private, curve=curve)
        self._can_encrypt = bool(private)
        self.__curve = curve

    @RawDataDecorator(ret=True, strict=True)
    def encrypt(self, source):
        return self._ecc.encrypt(source.export())

    @RawDataDecorator(ret=True, strict=True)
    def decrypt(self, source):
        return self._ecc.decrypt(source.export())

    def can_encrypt(self):
        '''
        Determines if this encryptor has the private key for encryption.

        >>> ecc = ECC(SAMPLE_KEY_PUBLIC, SAMPLE_KEY_PRIVATE, 'p184')
        >>> ecc.can_encrypt()
        True
        >>> from .encryptor import make
        >>> ecc = make(['ecc', SAMPLE_KEY_PUBLIC, None, 'p184'])
        >>> ecc.can_encrypt()
        False
        '''
        return self._can_encrypt

    def proto(self):
        return ['ecc', self.__curve]


# TODO: move it to an unit test
SAMPLE_KEY_PUBLIC = '#&M=6cSQ}m6C(hUz-7j@E=>oS#TL3F[F[a[q9S;RhMh+F#gP|Q6R}lhT_e7b'
SAMPLE_KEY_PRIVATE = '!!![t{l5N^uZd=Bg(P#N|PH#IN8I0,Jq/PvdVNi^PxR,(5~p-o[^hPE#40.<|'
