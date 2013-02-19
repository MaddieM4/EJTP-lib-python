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

__all__ = ['createFrame', 'RegisterFrame']

from ejtp.util.py2and3 import RawData, RawDataDecorator
from ejtp.frame.base import BaseFrame

# contains all type of frames known to ejtp
# keys are RawData of length 1
# values are subclasses from ejtp.frame.base.BaseFrame
_frametypes = {}

@RawDataDecorator(strict=True)
def createFrame(data, ancestors = []):
    '''
    Returns subclass of BaseFrame represented by data[0] or throws
    NotImplementedError if char is not registered.
    '''
    
    cls = _frametypes.get(data[0])
    if cls is None:
        raise NotImplementedError('%s is not registered' % data[0])
    return cls(data, ancestors)

class RegisterFrame(object):
    '''
    This class is used as a decorator for subclasses of BaseFrame

    >>> from ejtp.frame.base import BaseFrame
    >>> @RegisterFrame('x')
    ... class MyXFrame(BaseFrame):
    ...     pass
    ...
    '''

    def __init__(self, char):
        '''
        char is a RawData of length 1 (or convertible to RawData) that will represent
        the character used in raw transmission of frames.
        '''

        if not isinstance(char, RawData):
            try:
                char = RawData(char)
            except (TypeError, ValueError):
                raise TypeError('char must be convertible to RawData')
        
        if len(char) != 1:
            raise ValueError('char must be of length 1')
        
        if char in _frametypes:
            raise ValueError('char is already registered')
        
        self._char = char
    
    def __call__(self, cls):
        '''
        Gets called when the class is created.
        cls must be subclass of BaseFrame
        '''

        if not issubclass(cls, BaseFrame):
            raise TypeError('class must be subclass of BaseFrame')
        
        if self._char not in _frametypes:
            _frametypes[self._char] = cls
        
        return cls
