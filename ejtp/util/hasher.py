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

import json

from persei import RawData, String, RawDataDecorator, StringDecorator
from hashlib import new

HASH_FUNCTION = 'sha1' # was md5

@RawDataDecorator(strict=True)
@StringDecorator(args=False, ret=True, strict=True)
def make(string):
    '''
    Create a hash of a string.

    >>> make("Sample string")
    String('e9a47e5417686cf0ac5c8ad9ee90ba2c1d08cc14')
    '''
    return new(HASH_FUNCTION, string.export()).hexdigest()

def make6(string):
    return maken(string, 6)

def maken(string, n):
    return make(string)[:n]

@StringDecorator()
@StringDecorator(args=False, ret=True, strict=True)
def strict(obj=None):
    ''' Convert an object into a strict JSON string '''
    if isinstance(obj, bool) or obj==None or isinstance(obj, int):
        return json.dumps(obj)
    if isinstance(obj, String):
        return json.dumps(obj.export())
    if isinstance(obj, RawData):
        obj = tuple(obj)
    if isinstance(obj, list) or isinstance(obj, tuple):
        return "[%s]" % ",".join([strict(x).export() for x in obj])
    if isinstance(obj, dict):
        strdict = {}
        for key in obj:
            strdict[key] = obj[key]
        keys = sorted(strdict.keys())
        return "{%s}" % ",".join([strict(key).export()+":"+strict(strdict[key]).export() for key in keys])

@StringDecorator(strict=True)
def strictify(jsonstring):
    ''' Make a JSON string strict '''
    return strict(json.loads(jsonstring.export()))

def checksum(obj):
    ''' Get the checksum of the strict of an object '''
    return make(strict(obj))
