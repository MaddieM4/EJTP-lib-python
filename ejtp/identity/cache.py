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

from ejtp.address import *
from core import Identity

class IdentityCache(object):
    def __init__(self, source={}):
        self.cache = {}
        self.cache.update(source)

    def __contains__(self, location):
        location = str_address(location)
        return location in self.cache

    def __getitem__(self, location):
        return self.find_by_location(location)

    def __setitem__(self, location, value):
        '''
        Set an identity in the cache using dict syntax.

        >>> cache = IdentityCache()
        >>> ident = Identity("joe", ['rotate',3], ['local', None, 'joe'])

        There are some failsafes - you can only set to an Identity, at
        its location.

        >>> cache[ident.location] = []
        Traceback (most recent call last):
        TypeError: Expected ejtp.identity.core.Identity, got []

        >>> cache[ident.location.reverse()] = ident
        Traceback (most recent call last):
        ValueError: Trying to cache ident in the wrong location

        But if you actually do it right...

        >>> cache[ident.location] = ident
        >>> cache[ident.location] == ident
        True
        '''
        if not isinstance(value, Identity):
            raise TypeError(
                "Expected ejtp.identity.core.Identity, got %r" % value
            )
        location = str_address(location)
        if location != str_address(value.location):
            raise ValueError('Trying to cache ident in the wrong location')
        self.cache[location] = value

    def __delitem__(self, location):
        location = str_address(location)
        del self.cache[location]

    def update_ident(self, ident):
        self[str_address(ident.location)] = ident

    def find_by_name(self, name):
        for ident in self.cache.values():
            if ident.name == name:
                return ident
        raise KeyError(name)

    def find_by_location(self, location):
        #location = str_address(location)
        return self.cache[str_address(location)]

    def __repr__(self):
        return "<IdentityCache %r>" % repr(self.cache)

def sync_caches(*caches):
    sync = {}
    for c in caches:
        sync.update(c.cache)
    for c in caches:
        c.cache.update(sync)
