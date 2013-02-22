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

from ejtp.util.py2and3 import RawDataDecorator
from ejtp.address import py_address


class BaseJack(object):
    def __init__(self, address):
        self._address = py_address(address)
    
    @property
    def router_key(self):
        '''
        Returns unique identifier for storing in the router.
        '''
        raise NotImplementedError('subclasses of BaseJack must define router_key')


class ReaderJack(BaseJack):
    @property
    def router_key(self):
        return tuple(self._address[0:2])

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
