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

from persei import String

class IdentRef(object):
    '''
    Store a hashable reference to an Identity.

    This works like a glorified (key, cache) tuple, basically.
    '''
    def __init__(self, key, cache):
        self.key   = String(key)
        self.cache = cache

    def __eq__(self, other):
        return (self.key == other.key) and (self.cache == other.cache)

    def __hash__(self):
        return hash(self.key.export()) ^ hash(self.cache)

    def deref(self):
        return self.cache[self.key]
