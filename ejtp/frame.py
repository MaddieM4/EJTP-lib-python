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


'''
    Frame

    Class for EJTP frames.
'''

from ejtp.util import hasher
from ejtp.util.py2and3 import RawData, RawDataDecorator
from ejtp.address import *
import json

PACKET_SIZE = 8192

TYPES = {
    'j': RawData('j'),
    'r': RawData('r'),
    's': RawData('s'),
}

class Frame(object):
    @RawDataDecorator(strict=True)
    def __init__(self, data):
        self._load(data)

    def _load(self, data):
        self.type = data[0]
        sep = data.index('\x00')
        self.straddr = data[1:sep]
        self.ciphercontent = data[sep+1:]
        if self.type == TYPES['j']:
            self.raw_decode()
        if self.straddr:
            self.addr = json.loads(self.straddr.export())
            if (not isinstance(self.addr, list) or len(self.addr)<3):
                raise ValueError("Bad address: "+repr(self.addr))
        else:
            self.addr = None

    def __str__(self):
        return str(self.type+self.straddr+'\x00'+self.ciphercontent)

    def __repr__(self):
        return repr(str(self))

    def decode(self, encryptor):
        if not self.decoded:
            if self.type == TYPES['r']:
                self.content = encryptor.decrypt(self.ciphercontent.export())
            elif self.type == TYPES['s']:
                # Extract data
                self.sigsize   = int(self.ciphercontent[0])*256 + int(self.ciphercontent[1])
                self.signature = self.ciphercontent[2:self.sigsize+2]
                self.content   = self.ciphercontent[self.sigsize+2:]
                # Verify signature
                if not encryptor.sig_verify(self.content.export(), self.signature.export()):
                    raise ValueError("Invalid signature")
        return self.content

    def raw_decode(self):
        # Unencrypted content
        self.content = self.ciphercontent

    @property
    def jsoncontent(self):
        '''
        Get the Python-typed data represented by the frame content.

        >>> example = [ "hello", "world" ]
        >>> f = Frame("j\\x00" + json.dumps(example))
        >>> f.jsoncontent == example
        True
        '''
        if self.type == TYPES['j']:
            return json.loads(self.content.export())
        else:
            raise TypeError("Cannot get jsoncontent of frame with type!='j'")

    @property
    def decoded(self):
        return hasattr(self, "content")

@RawDataDecorator()
@RawDataDecorator(args=False, ret=True, strict=True)
def onion(msg, hops=[]):
    '''
        Encrypt a frame into multiple hops.

        Historically, this function supported splitting.
        At some future point we will put this functionality
        back in, but probably as a separate function.
    '''
    hops.reverse()
    for (addr, encryptor) in hops:
        msg = make(TYPES['r'], py_address(addr), encryptor, msg)
    return msg

@RawDataDecorator()
@RawDataDecorator(args=False, ret=True, strict=True)
def make(type, addr, encryptor, content):
    straddr = RawData()
    if addr != None:
        straddr = hasher.strict(addr)
    if encryptor:
        if type==TYPES['s']:
            signature = encryptor.sign(content.export())
            siglen = len(signature)
            ciphercontent = RawData(siglen // 256) + RawData(siglen % 256) + signature + content
        else:
            ciphercontent = encryptor.encrypt(content)
    else:
        ciphercontent = content
    msg = Frame(type+straddr+'\x00'+ciphercontent)
    msg.content = content
    return msg
