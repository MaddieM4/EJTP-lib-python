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

class BaseFrame(object):
    '''
    Base class for all frames.
    '''

    @RawDataDecorator(strict=True)
    def __init__(self, data):
        self._data = data
        self._decoded_data = None
        self._decoded = False
    
    def decode(self, ident_cache=None):
        '''
        decodes data to corresponding Python objects
        Must be defined by every subclass

        Arguments:
        ident_cache: IdentitiyCache that will be used while decoding.
                     If none is given, the Frame may fail to decode.
        '''
        raise NotImplementedError('each subclass of BaseFrame must define self.decode(ident_cache)')
    
    @property
    def content(self):
        if self._decoded:
            return self._decoded_data
        else:
            #TODO raise error
            pass 


class NestedFrame(BaseFrame):
    '''
    Base class for all frames containing another frame.
    '''
    
    def unpack(self, ident_cache=None):
        '''
        decodes, unpacks and returns the nested Frame.
        Must be defined by every subclass.

        Arguments:
        ident_cache: IdentitiyCache that will be used while decoding and unpacking.
                     If none is given, the Frame may fail to unpack.
        '''
        raise NotImplementedError('each subclass of BaseFrame must define self.unpack(ident_cache)')
