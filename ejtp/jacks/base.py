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

from ejtp.address import py_address
from ejtp.util.py2and3 import RawDataDecorator
import threading


class BaseJack(object):
    '''
    Base class for ReaderJack and WriterJack.

    Don't inherit from this class directly, use ReaderJack and WriterJack instead.

    Class attributes:
    has_local_address: indicates if this Jack class needs to bind to an address.
    '''
    has_local_address = False

    def __init__(self, address):
        '''
        Subclasses must call BaseJack.__init__ if it gets overridden.

        Arguments:
        address: valid EJTP address
        '''
        self._address = py_address(address)
        self._router = None
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._stop   = False
   
    def link(self, router):
        '''
        links jack to the given router.

        Also unlinks from the current router, if it is linked.

        Arguments:
        router: instance of ejtp.router.Router 
        '''
        from ejtp.router import Router
        if not isinstance(router, Router):
            raise ValueError('router must be instance of ejtp.router.Router')

        if self._router is not None:
            self.unlink()
 
        self._router = router
        self._router._load_jack(self)
   
    def unlink(self):
        '''
        unlinks jack from previous linked router.
        '''
        if self._router is not None:
            router = self._router
            self._router = None
            router.unload_jack(self)

    def connect(self, address):
        '''
        Return a Connection object that provides access to the given address.
        '''
        raise NotImplementedError('subclasses of BaseJack must define connect')
    
    def send(self, conn, data):
        '''
        Send data through a connection.
        '''
        raise NotImplementedError('subclasses of BaseJack must define send')

    def close_connection(self, conn):
        '''
        Close all sockets for a connection.
        '''
        raise NotImplementedError('subclasses of BaseJack must define close_connection')

    def _run(self):
        '''
        Blocking call for receiving new data.

        Incoming frames must be passed to self.recv.
        Must be overridden by subclasses, should regularly test for self._stop.
        '''
        raise NotImplementedError('subclasses of BaseJack must define _run')
    
    def run(self):
        ''' 
        Starts listening for incoming data.

        Internally, a new thread will run self._run and waits for data being yielded.
        The data then will be passed to self.router.recv.
        '''
        if self._thread.is_alive():
            raise JackRunningError()
        self._thread.start()

    def recv(self, data):
        '''
        Forward frame to router, if linked. Otherwise, silently drop that data.
        '''
        if self._router is not None:
            self._router.recv(data)

    def close(self):
        '''
        Shut down incoming connection server, all connections, and thread.
        '''
        for conn in self.connections:
            conn.close()
        self._stop = True
        self._thread.join()

    @property
    def router_key(self):
        '''
        Returns unique identifier for storing in the router.
        '''
        if not self.has_local_address:
            return (self._address[0], None)
        else:
            return tuple(self._address[0:2])


class JackRunningError(Exception):
    '''
    Gets raised if you try to start a ReaderJack that is currently running.
    '''
    pass


class ReaderJack(BaseJack):
    '''
    Base class of jacks that are capable of receiving connections.
    '''

    has_local_address = True

class WriterJack(BaseJack):
    '''
    Base class of jacks that are capable of creating connections.
    '''
    pass
