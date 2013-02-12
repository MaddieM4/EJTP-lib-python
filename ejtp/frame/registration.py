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

from ejtp.util.py2and3 import RawData
from ejtp.frame.base import BaseFrame

# contains all type of frames known to ejtp
# keys are RawData of length 1
# values are subclasses from ejtp.frame.base.BaseFrame
_frametypes = {}

class RegisterFrame(object):
    '''
    This class is used as a decorator for subclasses of BaseFrame
    '''

    def __init__(self, char):
        '''
        char is a RawData of length 1 (or convertible to RawData) that will represent
        the character used in raw transmission of frames.
        '''

        if not isinstance(char, RawData):
            char = RawData(char)
        
        if len(char) != 1:
            raise TypeError('char must be of length 1')
        
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
