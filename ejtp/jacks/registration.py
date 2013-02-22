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

__all__ = ['createJack', 'RegisterJack']
__doctestall__ = []

from ejtp.util.py2and3 import RawData, RawDataDecorator
from ejtp.address import py_address

# contains all types of jacks known to ejtp
# keys are the addrtype field of an address
# values are list of length 2: [readerJack, writerJack]
_jacktypes = {}

def createJack(address, reader = False):
    '''
    Returns instance of the Jack handling address throws
    ValueError if address is not registered.
    '''
    
    address = py_address(address)
    jacktype = _jacktypes.get(address[0])
    if jacktype is None:
        raise ValueError('%s is not registered' % address[0])
    cls = jacktype[0 if reader else 1]
    if cls is None:
        raise ValueError('%s for %s is not registered' % ('reader' if reader else 'writer', address[0]))
    return cls(address)


class RegisterJack(object):
    '''
    This class is used as a decorator for reader and writer Jacks

    >>> from ejtp.frame.base import BaseFrame
    >>> @RegisterFrame('x')
    ... class MyXFrame(BaseFrame):
    ...     pass
    ...
    '''

    @RawDataDecorator(strict=True)
    def __init__(self, addrtype):
        '''
        addrtype is the addrtype field of an address that will be mapped
        to the Jack.
        reader indicates if you are registering a reader or a writer.
        writer_nobind indicates if the writer has to bind it's address
        '''

        self._oldtype = _jacktypes.get(addrtype, [None, None])
        self._addrtype = addrtype
    
    def __call__(self, cls):
        '''
        Gets called when the class is created.
        cls must be subclass of BaseJack
        '''

        if not (issubclass(cls, ReaderJack) or issubclass(cls, WriterJack)):
            raise TypeError('class must be subclass of ReaderJack or WriterJack')
        
        newtype = [None, None]
        if issubclass(cls, ReaderJack):
            if self._oldtype[0] is not None:
                raise ValueError('reader for %s already registered' % self._addrtype)
            newtype[0] = cls
        if issubclass(cls, WriterJack):
            if self._oldtype[1] is not None:
                raise ValueError('writer for %s already registered' % self._addrtype)
            newtype[1] = cls
        
        _jacktypes[self._addrtype] = newtype

        return cls
