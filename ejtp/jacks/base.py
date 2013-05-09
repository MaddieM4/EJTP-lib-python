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
from ejtp.router import Router
from ejtp.util.py2and3 import RawDataDecorator
import threading


class BaseJack(object):
    '''
    Base class for ReaderJack and WriterJack.

    Don't inherit from this class directly, use ReaderJack and WriterJack instead.

    Class attributes:
    bind: indicates if this Jack class needs to bind to an address.
    '''
    bind = False

    def __init__(self, address):
        '''
        Subclasses must call BaseJack.__init__ if it gets overridden.

        Arguments:
        address: valid EJTP address
        '''
        self._address = py_address(address)
        self._router = None
   
    def link(self, router):
        '''
        links jack to the given router.

        Also unlinks from the current router, if it is linked.

        Arguments:
        router: instance of ejtp.router.Router 
        '''
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
            self._router.unload_jack(self, True)
            self._router = None
    
    @property
    def router_key(self):
        '''
        Returns unique identifier for storing in the router.
        '''
        if not self.bind:
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
    Base class of jacks that are capable of receiving data.
    '''

    bind = True

    def __init__(self, *args):
        BaseJack.__init__(self, *args)
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        '''
        Blocking call for receiving new data.

        Incoming frames must be passed to self.recv.
        Must be overridden by subclasses.
        '''
        raise NotImplementedError('subclasses of ReaderJack must define _run')
    
    def run(self):
        ''' 
        Starts listening for incoming data.

        Internally, a new thread will run self._run and waits for data being yielded.
        The data then will be passed to self.recv.
        '''
        if self._thread.is_alive():
            raise JackRunningError()
        self._thread.start()

    def recv(self, frame):
        '''
        Gets called in self._run() and passes the frame to the router.

        If no router is loaded, the frame will be discarded.

        Arguments:
        frame: a frame returned by ejtp.frame.createFrame
        '''
        if self._router is None:
            #TODO: log this
            # frame gets discarded here
            return
        
        self._router.recv(frame)


class WriterJack(BaseJack):
    '''
    Base class of jacks that are capable of sending data.
    '''

    @RawDataDecorator(strict=True)
    def send(self, data):
        '''
        Sends data to address.
        '''
        raise NotImplementedError('subclasses of WriterJack must define send')
