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
from ejtp.address import *
import json

PACKET_SIZE = 8192

class Frame(object):
    def __init__(self, data):
        if type(data) in (str, unicode, Frame):
            data = str(data)
            self._load(data)

    def _load(self, data):
        self.type = data[0]
        sep = data.index('\x00')
        self.straddr = data[1:sep]
        self.ciphercontent = data[sep+1:]
        if self.type =="j":
            self.raw_decode()
        if self.straddr:
            self.addr = json.loads(self.straddr)
            if (type(self.addr) != list or len(self.addr)<3):
                raise ValueError("Bad address: "+repr(self.addr))
        else:
            self.addr = None

    def __str__(self):
        return self.type+self.straddr+'\x00'+self.ciphercontent

    def __repr__(self):
        return repr(str(self))

    def decode(self, encryptor):
        if not self.decoded:
            if self.type == "r":
                self.content = encryptor.decrypt(self.ciphercontent)
            elif self.type == "s":
                # Extract data
                self.sigsize   = ord(self.ciphercontent[0])*256 + ord(self.ciphercontent[1])
                self.signature = self.ciphercontent[2:self.sigsize+2]
                self.content   = self.ciphercontent[self.sigsize+2:]
                # Verify signature
                if not encryptor.sig_verify(self.content, self.signature):
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
        if self.type == "j":
            return json.loads(self.content)
        else:
            raise TypeError("Cannot get jsoncontent of frame with type %r" % self.type)

    @property
    def decoded(self):
        return hasattr(self, "content")

def onion(msg, hops=[]):
    '''
        Encrypt a frame into multiple hops.

        Historically, this function supported splitting.
        At some future point we will put this functionality
        back in, but probably as a separate function.
    '''
    hops.reverse()
    for (addr, encryptor) in hops:
        msg = str(make('r', py_address(addr), encryptor, str(msg)))
    return msg

def make(type, addr, encryptor, content):
    straddr = ""
    if addr != None:
        straddr = hasher.strict(addr)
    if encryptor:
        if type=='s':
            signature = encryptor.sign(content)
            siglen = len(signature)
            ciphercontent = chr(siglen // 256) + chr(siglen % 256) + signature + content
        else:
            ciphercontent = encryptor.encrypt(content)
    else:
        ciphercontent = content
    msg = Frame(type +straddr+'\x00'+ciphercontent)
    msg.content = content
    return msg
