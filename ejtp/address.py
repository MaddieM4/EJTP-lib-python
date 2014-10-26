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
import warnings

from json import loads

from persei import String, StringDecorator

from ejtp.util.hasher import strict

from collections import namedtuple

@StringDecorator()
def str_address(address):
    '''
        Converts address to string, only if it isn't already
        >>> str_address([0,9])
        '[0,9]'
        >>> str_address("[0,9]")
        '[0,9]'
    '''
    warnings.warn("don't use str_address, it will be removed soon! Use Address instead.", DeprecationWarning)
    if isinstance(address, String):
        return address
    else:
        return strict(address)

@StringDecorator()
def py_address(address):
    '''
        Converts address to non-string, only if it isn't already
        >>> py_address([0,9])
        [0, 9]
        >>> py_address("[0,9]")
        [0, 9]
    '''
    warnings.warn("don't use py_address, it will be removed soon! Use Address instead.", DeprecationWarning)
    if isinstance(address, String):
        return loads(address.export())
    elif isinstance(address, list):
        return address
    elif isinstance(address, tuple):
        return loads(strict(address).export())
    else:
        raise ValueError("Can not convert to py_address: %r" % address)

class Address(namedtuple('_Address', ('addrtype', 'addrdetails', 'callsign'))):
    '''
    Represents an Address in EJTP.
    
    There are 3 fields: addrtype, addrdetails and callsign.
    addrtype is the jack type that will be used (e.g. 'udp' or 'tcp6')
    addrdetails are additional protocol specific parameters
    callsign is used to identify different clients on the same jack. They only
    get used by Clients.
    '''
    __slots__ = ()

    def __new__(cls, addrtype, addrdetails=None, callsign=None):
        return super(Address, cls).__new__(cls, addrtype, addrdetails, callsign)

    @classmethod
    @StringDecorator()
    def create(cls, address):
        '''
        Create address from a json string, a list, or a tuple.
        '''
        if isinstance(address, String):
            addr = loads(address.export())
        elif isinstance(address, list):
            addr = address
        elif isinstance(address, tuple):
            addr = loads(strict(address).export())
        elif isinstance(address, str):
            addr = loads(strict(address))
        else:
            raise TypeError("Can not create Address object: %r" % address)

        if len(addr) < 1 or len(addr) > 3:
            raise ValueError('invalid address format')
        return cls(*addr)
    
    def export(self):
        '''
        Returns address as json string.
        '''
        return strict(self)
