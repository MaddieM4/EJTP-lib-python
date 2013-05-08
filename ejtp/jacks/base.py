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


class ReaderJack(BaseJack):
    '''
    Base class of jacks that are capable of receiving data.
    '''

    def run(self):
        raise NotImplementedError('subclasses of ReaderJack must define run')
    
    @RawDataDecorator(strict=True)
    def recv(self, data):
        '''
        Gets called in self.run() and passes the data to the router
        '''
        pass 


class WriterJack(BaseJack):
    nobind = True

    @property
    def router_key(self):
        if self.nobind:
            return (self._address[0], None)
        else:
            return tuple(self._address[0:2])

    @RawDataDecorator(strict=True)
    def send(self, data):
        '''
        Sends data to address.
        '''
        raise NotImplementedError('subclasses of WriterJack must define send')
