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

from ejtp.jacks import core as jack

import threading
try:
    import Queue
except ImportError: # in python3.x it's renamed to lowercase queue
    import queue as Queue

class StreamJack(jack.Jack):
    def __init__(self, router, interface):
        jack.Jack.__init__(self, router, interface)
        self.connections = {}

    # SUBCLASS INTERFACE ------------------------------------------------------

    def label(self, interface):
        '''
        Determine the key for self.connections, or "label", that would be appropriate
        for a message going to the address listed in the interface variable.
        '''
        pass

    def create_connection(self, interface):
        '''
        Create a connection to contact an interface.

        Return the connection, and it will be added to self.connections.
        '''
        pass

    # def run(self): pass
    # def close(self): pass

    # PROVIDED BY BASE CLASS --------------------------------------------------

    def add_connection(self, interface, conn=None):
        '''
        Create a connection, add it to self.connections, and return it.
        '''
        if conn==None:
            conn = self.create_connection(interface)
        label = self.label(interface)
        self.connections[label] = conn
        return conn

    def get_connection(self, interface):
        '''
        Retrieve or create a connection as necessary.
        '''
        label = self.label(interface)
        if label in self.connections:
            return self.connections[label]
        else:
            return self.add_connection(interface)

    def route(self, frame):
        '''
        Send frame to somewhere.
        '''
        conn = self.get_connection(frame.address)
        conn.send(frame)

class Connection(object):
    '''
    Represents a persistent connection to a remote host. Should be subclassed.
    '''
    def __init__(self, jack=None):
        self.jack = jack
        self._buffer = RawData()
        self._running = False
        self._outqueue = Queue.Queue()
        self._thread = threading.Thread(target=self.run)

    # SUBCLASS INTERFACE ------------------------------------------------------

    @RawDataDecorator(strict=True)
    def _send(self, frame):
        '''
        Subclass-provided function that sends text to the remote end.
        '''
        pass

    @RawDataDecorator(args=False, ret=True, strict=True)
    def _recv(self):
        '''
        Subclass-provided function that returns text. Allowed to block.
        '''
        pass

    def run(self):
        '''
        Network recieve loop.
        '''
        pass

    # PROVIDED BY BASE CLASS --------------------------------------------------

    def start(self):
        self._running = True
        self._thread.start()

    def close(self):
        self._running = False

    def send(self, frame):
        self._send(self.wrap(frame.content))

    def recv(self, timeout=0):
        '''
        Retrieve from output queue without blocking. Returns None or str.

        The output queue is only used if self.jack == None.
        '''
        try:
            return self._outqueue.get(timeout=timeout)
        except Queue.Empty:
            return None

    def wrap(self, frame):
        '''
        Wrap a frame for transport
        '''
        return RawData(format(len(frame), '0x')) + "." + frame        

    @RawDataDecorator(strict=True)
    def inject(self, newdata):
        '''
        Process new data from the outside world.
        '''
        self._buffer += newdata
        if RawData(".") not in self._buffer:
            return
        size, content = self._buffer.split('.',1)
        size = int(size.export(), 16) # Read size as hex
        if len(content) < size:
            return
        if self.jack:
            self.jack.recv(content[:size])
        else:
            self._outqueue.put(content[:size])
        self._buffer = content[size:]
