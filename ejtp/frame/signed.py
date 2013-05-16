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
from ejtp.frame.address import SenderCategory

@RegisterFrame('s')
class SignedFrame(SenderCategory, BaseFrame):
    @RawDataDecorator(args=False, ret=True, strict=True)
    def decode(self, ident_cache):
        try:
            ident = ident_cache[self.address]
        except (KeyError, TypeError):
            raise ValueError('could not load Identity from ident_cache')
        body = self.body
        sigsize = int(body[0]) * 256 + int(body[1])
        content = body[sigsize+2:]
        if not ident.verify_signature(body[2:sigsize+2], content):
            raise ValueError('Invalid signature')
        return content

def construct(identity, content):
    signature = identity.sign(content)
    siglen = len(signature)

    return SignedFrame(
        RawData('s') + \
        RawData(str_address(identity.location)) + \
        RawData((0, siglen // 256, siglen % 256)) + \
        RawData(signature) + \
        RawData(content)
    )
