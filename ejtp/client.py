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

from persei import RawData, RawDataDecorator, StringDecorator

from ejtp.crypto.encryptor import make
from ejtp.util.hasher import strict, make as hashfunc

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
        if isinstance(msg, frame.address.ReceiverCategory):
            if msg.address != self.interface:
                self.relay(msg)
            else:
                self.route( msg.unpack(self.encryptor_cache) )
        elif isinstance(msg, frame.address.SenderCategory):
            self.route( msg.unpack(self.encryptor_cache) )
        elif isinstance(msg, frame.json.JSONFrame):
            self.rcv_callback(msg, self)
        else:
            raise TypeError("Unknown frame type", msg)

    def rcv_callback(self, msg, client_obj):
        logger.info("Client %r recieved from %r: %r", client_obj.interface, msg.sender, msg)

    def write(self, addr, txt, wrap_sender=True):
        # Write and send a frame to addr
        self.owrite([addr], txt, wrap_sender)

    def owrite(self, hoplist, msg, wrap_sender=True):
        # Write a frame and send through a list of addresses
        # The "o" is for onion routing
        if wrap_sender:
            msg = self.wrap_sender(msg)
        # Onion routing magic
        for address in reversed(hoplist):
            ident = self.encryptor_cache[str_address(address)]
            msg = frame.encrypted.construct(ident, msg.content)
        self.send(msg)

    def owrite_json(self, hoplist, data, wrap_sender=True):
        msg = frame.json.construct(data)
        self.owrite(hoplist, msg, wrap_sender)

    def write_json(self, addr, data, wrap_sender=True):
        self.owrite_json([addr], data, wrap_sender)

    def wrap_sender(self, msg):
        # Encapsulate a message within a sender frame
        return frame.signed.construct(self.identity, msg.content)

    @property
    def identity(self):
        return self.encryptor_cache[self.interface]

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

