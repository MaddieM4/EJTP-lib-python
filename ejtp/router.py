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
from ejtp.util.crashnicely import Guard

STOPPED = 0
THREADED = 1

class Router(object):
    def __init__(self, jacks=[], clients=[]):
        self.runstate = STOPPED
        self._jacks = {}
        self._clients = {}
        self._loadjacks(jacks)
        self._loadclients(clients)
        self.run()

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
            recvr = self.client(msg.address) or self.jack(msg.address)
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

    def kill_client(self, addr):
        addr = rtuple(addr[:3])
        del self._clients[addr] # Bubble exception up if client does not exist

    def thread_all(self):
        # Run all Jack threads
        for i in self._jacks:
            self._jacks[i].run_threaded()

    def stop_all(self):
        # Run all Jack threads
        for i in self._jacks:
            self._jacks[i].close()

    def run(self, level=THREADED):
        if level==THREADED:
            if self.runstate == STOPPED:
                self.thread_all()
        elif level==STOPPED:
            # stop all jacks
            self.stop_all()
        self.runstate = level

    def _loadjacks(self, jacks):
        for j in jacks:
            self._loadjack(j)

    def _loadclients(self, clients):
        for c in clients:
            self._loadclient(c)

    def _loadjack(self, jack):
        key = rtuple(jack.interface[:2])
        if key in self._jacks:
            raise ValueError('jack already loaded')
        self._jacks[key] = jack
        if self.runstate == THREADED:
            jack.run_threaded()

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
