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

from   ejtp.address import *

class IdentityCache(object):
    def __init__(self, source={}):
        self.cache = {}
        self.cache.update(source)

    def __getitem__(self, location):
        return self.find_by_location(location)

    def __setitem__(self, location, value):
        location = str_address(location)
        self.cache[location] = value

    def __delitem__(self, location):
        location = str_address(location)
        del self.cache[location]

    def update_ident(self, ident):
        self[ident.location] = ident

    def find_by_name(self, name):
        for ident in self.cache.values():
            if ident.name == name:
                return ident
        raise KeyError(name)

    def find_by_location(self, location):
        location = str_address(location)
        return self.cache[location]

    def __repr__(self):
        return "<IdentityCache %r>" % repr(self.cache)

def sync_caches(*caches):
    sync = {}
    for c in caches:
        sync.update(c.cache)
    for c in caches:
        c.cache.update(sync)
