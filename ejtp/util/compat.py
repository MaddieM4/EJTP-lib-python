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

import sys

if (2, 7) <= sys.version_info[:2] < (3, 0) or sys.version_info >= (3, 2):
    import unittest
else:
    import unittest2 as unittest

try:
    import json
except ImportError:
    import simplejson as json

# Same as sys.version_info.major, but supports pre-2.7
is_py3k = sys.version_info[0] == 3

def get_exception():
    return sys.exc_info()[1]

# Python 2.5 does not have format builtin
try:
    format = format
except NameError:
    def format(value, spec): # TODO: is it right?
        f ='%' + spec
        return f % value

# Python 2.5 does not have bytes builtin
try:
    bytes = bytes
except NameError:
    bytes = str
