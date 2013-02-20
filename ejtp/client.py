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

import logging
logger = logging.getLogger(__name__)

from ejtp.crypto.encryptor import make
from ejtp.util.hasher import strict, make as hashfunc
from ejtp.util.py2and3 import RawData, RawDataDecorator, StringDecorator

from ejtp.address import *
from ejtp import frame
from ejtp import jacks
from ejtp import identity

class Client(object):
    def __init__(self, router, interface, encryptor_cache = None, make_jack = True):
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
            jacks.make(router, interface)

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
        msg = frame.json.construct(data)
        self.owrite(hoplist, msg, wrap_sender)

    def write_json(self, addr, data, wrap_sender=True):
        self.owrite_json([addr], data, wrap_sender)

    def wrap_sender(self, msg):
        # Encapsulate a message within a sender frame
        sig_s = self.encryptor_get(self.interface)
        msg   = frame.createFrame('t', str_address(self.interface) sig_s, msg.bytes())
        return msg

    # Encryption

    def encryptor_get(self, address):
        address = str_address(address)
        return make(self.encryptor_cache[address].encryptor)

    def encryptor_set(self, address, encryptor):
        address = py_address(address)
        if not address in self.encryptor_cache:
            dummy_ident = identity.Identity(None, encryptor, address)
            self.encryptor_cache.update_ident(dummy_ident)
        else:
            self.encryptor_cache[address].encryptor = list(encryptor)

    def sign(self, obj):
        '''
        Make a signature with this client's interface.
        '''
        strdata = hashfunc(strict(obj))
        return self.encryptor_get(self.interface).flip().encrypt(strdata)

    def sig_verify(self, obj, signer, sig):
        '''
        Verify a signature.
        '''
        strdata = hashfunc(strict(obj))
        return self.encryptor_get(signer).flip().decrypt(sig).toString() == strdata

