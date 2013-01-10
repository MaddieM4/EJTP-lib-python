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

def is_string(value):
    '''
    Checks, if value is a string. In python 2.x it checks if value is an
    instance of basestring. In python 3.x it checks if it is an instance of
    str or bytes, since all strings in python 3 derivate from str rather than
    basestring and bytes isn't a subclass of str anymore.

    '''

    if isinstance(value, str):
        return True
    if bytes == str:
        # In python 2.x bytes is equal with str, in python 3.x not.
        return isinstance(value, basestring)
    return isinstance(value, bytes)

def get_unicode():
    '''
    Returns an unicode class. In python 2.x thats unicode but in python 3.x
    there is no uncode class anymore, because str itself is unicode.
    '''

    if bytes == str:
        return unicode
    return str

class RawData(object):
    '''
    This class is supposed to store raw data and behaves similar to str in
    python 2.x and bytes in python 3.x
    '''
    def __init__(self, value=()):
        '''
        Takes an iterable value that should contain either integers in range(256)
        or corresponding characters.

        >>> repr(RawData((1, 2, 3))) == '010203'
        True
        >>> repr(RawData(('a', 'b', 'c'))) == '616263'
        True
        >>> RawData((70, 71, 72)).to_string() == 'FGH'
        True
        '''
        try:
            iter(value)
        except TypeError:
            raise TypeError('value must be iterable')
        try:
            for c in value:
                if ord(c) > 255:
                    raise ValueError('values not in range(256)')
            self._data = tuple([ord(c) for c in value])
        except TypeError:
            # value may be an iterable of ints
            try:
                for i in value:
                    if i < 0 or i > 255:
                        raise ValueError('values not in range(256)')
                self._data = tuple(value)
            except TypeError:
                raise TypeError('value must contain integers in range(256) or corresponding characters')
            
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._data == other._data
        return False

    def __add__(self, other):
        if isinstance(other, type(self)):
            return type(self)(self._data + other._data)
        if isinstance(other, int):
            return type(self)(self._data + (other,))
        raise NotImplemented
    
    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __iter__(self):
        return self._data.__iter__()

    def __repr__(self):
        return get_unicode()().join([format(c, '02x') for c in self._data])
    
    def to_string(self):
        if bytes == str:
            return get_unicode()().join([unichr(c) for c in self._data])
        return get_unicode()().join([chr(c) for c in self._data])

String = get_unicode()
