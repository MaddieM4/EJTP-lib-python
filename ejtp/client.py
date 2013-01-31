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

from ejtp import logging
logger = logging.getLogger(__name__)

from ejtp.crypto.encryptor import make
from ejtp.util.hasher import strict, make as hashfunc
from ejtp.util.py2and3 import RawDataDecorator, StringDecorator

from ejtp.address import *
from ejtp import frame
from ejtp import jacks
from ejtp import identity

class Client(object):
    def __init__(self, router, interface, encryptor_cache = None, make_jack = True, compression = True):
        '''
            encryptor_get should be a function that accepts an argument "iface"
            and returns an encryptor prototype (2-element list, like ["rotate", 5]).
        '''
        self.interface = (interface and py_address(interface)) or interface
        self.router = router
        if hasattr(self.router, "_loadclient"):
            self.router._loadclient(self)
        self.encryptor_cache = encryptor_cache or identity.IdentityCache()
        if make_jack:
            jacks.make(router, interface, compression)

    def send(self, msg):
        # Send frame to router
        self.router.recv(msg)

    def relay(self, msg):
        '''
        Relay unwrapped frame. For basic clients, this is just self.send, but
        it's a very convenient spot to override stuff in more complex subclasses.
        '''
        self.send(msg)

    def route(self, msg):
        # Recieve frame from router (will be type 'r' or 's', which contains message)
        logger.debug("Client routing frame: %s", repr(msg))
        if msg.type == msg.T_R:
            if msg.addr != self.interface:
                self.relay(msg)
            else:
                self.route(self.unpack(msg))
        elif msg.type == msg.T_S:
            self.route(self.unpack(msg))
        elif msg.type == msg.T_J:
            self.rcv_callback(msg, self)

    def rcv_callback(self, msg, client_obj):
        logger.info("Client %r recieved from %r: %r", client_obj.interface, msg.addr, msg.content)

    def unpack(self, msg):
        # Return the frame inside a Type R or S
        encryptor = self.encryptor_get(msg.addr)
        if encryptor == None:
            msg.raw_decode()
        else:
            msg.decode(encryptor)
        result = frame.Frame(msg.content)
        if result.addr == None:
            result.addr = msg.addr
        return result

    def write(self, addr, txt, wrap_sender=True):
        # Write and send a frame to addr
        self.owrite([addr], txt, wrap_sender)

    def owrite(self, hoplist, msg, wrap_sender=True):
        # Write a frame and send through a list of addresses
        # The "o" is for onion routing
        if wrap_sender:
            msg = self.wrap_sender(msg)
        hoplist = [(a, self.encryptor_get(a)) for a in hoplist]
        self.send(frame.onion(msg, hoplist))

    def owrite_json(self, hoplist, data, wrap_sender=True):
        msg = frame.make(frame.Frame.T_J, None, None, strict(data))
        self.owrite(hoplist, msg, wrap_sender)

    def write_json(self, addr, data, wrap_sender=True):
        self.owrite_json([addr], data, wrap_sender)

    def wrap_sender(self, msg):
        # Encapsulate a message within a sender frame
        sig_s = self.encryptor_get(self.interface)
        msg   = frame.make(frame.Frame.T_S, self.interface, sig_s, msg.bytes())
        return msg

    # Encryption

    def encryptor_get(self, address):
        address = str_address(address)
        return make(self.encryptor_cache[address].encryptor)

    def encryptor_set(self, address, encryptor):
        '''
        >>> client = mock_client()
        >>> client.encryptor_set(["x", ["y", 8], "z"], ['rotate', 4])
        >>> e = client.encryptor_get('["x",["y",8],"z"]')
        >>> e #doctest: +ELLIPSIS
        <ejtp.crypto.rotate.RotateEncryptor object ...>
        >>> from ejtp.util.py2and3 import RawData
        >>> e.encrypt("Aquaboogie") == RawData('Euyefsskmi')
        True
        '''
        address = py_address(address)
        if not address in self.encryptor_cache:
            dummy_ident = identity.Identity(None, encryptor, address)
            self.encryptor_cache.update_ident(dummy_ident)
        else:
            self.encryptor_cache[address].encryptor = list(encryptor)

    def sign(self, obj):
        '''
        Make a signature with this client's interface.
        
        >>> c = Client(None, ['demo_interface'])
        >>> c.encryptor_set(c.interface, ['rotate',41])
        >>> original = ['catamaran']
        >>> c.sign(original)
        RawData(3a0a0e3b3c39100e0f3d3a380b0c0d0807390f0f0c390e0e083d3a383a3a0b10393d0b090c3a0a0b)
        '''
        strdata = hashfunc(strict(obj))
        return self.encryptor_get(self.interface).flip().encrypt(strdata)

    def sig_verify(self, obj, signer, sig):
        '''
        Verify a signature.
        
        >>> c = Client(None, ['demo_interface'])
        >>> c.encryptor_set(c.interface, ['rotate',41])
        >>> original = ['catamaran']
        >>> c.sig_verify(original, c.interface, c.sign(original))
        True
        '''
        strdata = hashfunc(strict(obj))
        return self.encryptor_get(signer).flip().decrypt(sig).toString() == strdata

def mock_client():
    return Client(None, None, make_jack=False)

def mock_locals(name1="c1", name2="c2"):
    '''
    Returns two clients that talk locally through a router.
    >>> c1, c2 = mock_locals()
    >>> c1.encryptor_cache = c2.encryptor_cache # Let's only set this stuff once
    >>> c1.encryptor_set(c1.interface, ['rotate',  3])
    >>> c1.encryptor_set(c2.interface, ['rotate', -7])
    >>> c1.router == c2.router
    True
    >>> c1.write_json(c2.interface, "hello") # doctest: +ELLIPSIS
    INFO:ejtp.client: Client ['udp', ['127.0.0.1', 555], 'c2'] recieved from [...'udp', [...'127.0.0.1', 555], ...'c1']: RawData(2268656c6c6f22)
    >>> c2.write_json(c1.interface, "goodbye") # doctest: +ELLIPSIS
    INFO:ejtp.client: Client ['udp', ['127.0.0.1', 555], 'c1'] recieved from [...'udp', [...'127.0.0.1', 555], ...'c2']: RawData(22676f6f6462796522)
    '''
    from ejtp.router import Router
    r  = Router()
    c1 = Client(r, ['udp', ['127.0.0.1', 555], name1], make_jack = False)
    c2 = Client(r, ['udp', ['127.0.0.1', 555], name2], make_jack = False)
    return (c1, c2)
