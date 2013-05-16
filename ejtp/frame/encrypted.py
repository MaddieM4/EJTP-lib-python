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

from persei import RawData, RawDataDecorator

from ejtp.address import str_address
from ejtp.frame.base import BaseFrame
from ejtp.frame.registration import RegisterFrame
from ejtp.frame.address import ReceiverCategory

@RegisterFrame('r')
class EncryptedFrame(ReceiverCategory, BaseFrame):
    @RawDataDecorator(args=False, ret=True, strict=True)
    def decode(self, ident_cache):
        try:
            ident = ident_cache[self.address]
        except (KeyError, TypeError):
            raise ValueError('could not load Identity from ident_cache')
        return ident.decrypt(self.body)

def construct(identity, content):
    return EncryptedFrame(
        RawData('r') + \
        RawData(str_address(identity.location)) + \
        RawData((0,)) + \
        RawData(identity.encryptor.encrypt(content))
    )
