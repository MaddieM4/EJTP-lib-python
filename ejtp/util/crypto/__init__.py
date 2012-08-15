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


__all__ = [
	'aes',
    'encryptor',
	'rsa',
	'rotate',
]

from encryptor import make

def bin_unicode(string):
    '''
    Turn binary data into serialized unicode.

    >>> evilstr = chr(186) + chr(129) + chr(200)
    >>> bin_unicode(evilstr)
    u'\\xba\\x81\\xc8'
    '''
    return unicode().join(unichr(ord(x)) for x in string)

def bin_string(ustring):
    '''
    Turn binary data into serialized str.

    >>> evilstr = chr(186) + chr(129) + chr(200)
    >>> unicorn = bin_unicode(evilstr)
    >>> unicorn
    u'\\xba\\x81\\xc8'
    >>> str(unicorn)
    Traceback (most recent call last):
    UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-2: ordinal not in range(128)
    >>> bin_string(unicorn)
    '\\xba\\x81\\xc8'
    >>> evilstr
    '\\xba\\x81\\xc8'
    >>> bin_string(unicorn) == evilstr
    True
    '''
    return str().join(chr(ord(x)) for x in ustring)
