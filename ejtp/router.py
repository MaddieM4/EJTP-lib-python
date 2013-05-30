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
    EJTP Router.

    This virtual device takes jacks on one side for external communication,
    and clients on the other side for internal frame routing.
'''

import logging
logger = logging.getLogger(__name__)

from ejtp import frame
from ejtp.jacks import createJack
from ejtp.jacks.base import BaseJack
from ejtp.util.crashnicely import Guard

STOPPED = 0
THREADED = 1

class Router(object):
    def __init__(self, jacks=[], clients=[]):
        self._jacks = {}
        self._clients = {}
        self._connections = {}
        self.load_jacks(jacks)
        self._loadclients(clients)

    def recv(self, msg):
        '''
        Accepts string or frame.Frame

        In the future, we may want to consider non-frames a ValueError
        '''
        logger.debug("Handling frame: %s", repr(msg))
        if not isinstance(msg, frame.base.BaseFrame):
            try:
                msg = frame.createFrame(msg)
            except Exception:
                logger.info("Router could not parse frame: %s", repr(msg))
                return
        if isinstance(msg, frame.address.ReceiverCategory):
            recvr = self.client(msg.address) or self.connection(msg.address)
            if recvr:
                with Guard():
                    recvr.route(msg)
            else:
                logger.info("Router could not deliver frame: %s", str(msg.address))
        elif isinstance(msg, frame.address.SenderCategory):
            logger.info("Frame recieved directly from %s", str(msg.address))
        else:
            logger.info("Frame has a type that the router does not understand (%r)", msg)

    def jack(self, addr):
        # Return jack registered at addr, or None
        for (t, l) in self._jacks:
            if t == addr[0]:
                return self._jacks[(t,l)]
        return None

    def client(self, addr):
        # Return client registered at addr, or None
        addr = rtuple(addr[:3])
        if addr in self._clients:
            return self._clients[addr]
        else:
            return None

    def connection(self, addr):
        addr = rtuple(addr[:2])
        if addr in self._connections:
            return self._connections[addr]
        else:
            return None

    def connect(self, address):
        '''
        Create and register a Connection to the given address.
        '''
        jack = self.create_jack(address)
        conn = jack.connect(address)
        self.load_connection(conn)
        return conn

    def create_jack(self, address):
        '''
        Create and register a WriterJack, if necessary.
        '''
        registered = self.jack(addr)
        if registered:
            return registered
        else:
            # Create and register new Jack
            jack = createJack(address)
            self.load_jack(jack)
            return jack

    def load_jack(self, jack):
        '''
        loads jack into router.

        If jack was already loaded, it gets unloaded and reloaded instead.

        Arguments:
        jack: instance of ejtp.jacks.base.BaseJack

        Raises:
        TypeError: if jack is not a valid jack
        '''
        if not isinstance(jack, BaseJack):
            raise TypeError('jack must be instance of BaseJack')
        jack.link(self)

    def load_jacks(self, jacks):
        '''
        Convenient call for loading multiple jacks at once.

        Arguments:
        jacks: iterable that contains instances of ejtp.jacks.base.BaseJack
        '''
        for j in jacks:
            self.load_jack(j)
    
    def unload_jack(self, jack):
        '''
        unloads jack from router.

        Arguments:
        jack: instance of ejtp.jacks.base.BaseJack

        Raises:
        TypeError: if jack is not a valid jack
        ValueError: if jack is not loaded in this router
        '''
        if not isinstance(jack, BaseJack):
            raise TypeError('jack must be instance of BaseJack')
        if jack.router_key not in self._jacks:
            raise ValueError('jack is not loaded in router')
        jack.unlink()

    def kill_client(self, addr):
        addr = rtuple(addr[:3])
        del self._clients[addr] # Bubble exception up if client does not exist
   
    def _load_jack(self, jack):
        '''
        loads jack into router.

        Arguments:
        jack: instance of ejtp.jacks.base.BaseJack
        '''
        self._jacks[jack.router_key] = jack
    
    def _unload_jack(self, jack):
        '''
        unloads jack from router.

        If jack was not loaded in this router, this method returns silently.

        Arguments:
        jack: instance of ejtp.jacks.base.BaseJack
        '''
        if jack.router_key in self._jacks:
            del self._jacks[jack.router_key]

    def load_connection(self, conn):
        addr = rtuple(conn.remote[:2])
        self._connections[addr] = conn

    def unload_connection(self, conn):
        addr = rtuple(conn.remote[:2])
        del self._connections[addr]
        conn.close()

    def _loadclients(self, clients):
        for c in clients:
            self._loadclient(c)

    def _loadclient(self, client):
        key = rtuple(client.interface[:3])
        if key in self._clients:
            raise ValueError('client already loaded')
        self._clients[key] = client

def rtuple(obj):
    # Convert lists into tuples recursively
    if isinstance(obj, list) or isinstance(obj, tuple):
        return tuple([rtuple(i) for i in obj])
    else:
        return obj
