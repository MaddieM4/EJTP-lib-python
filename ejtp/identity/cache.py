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

from persei import String, StringDecorator, JSONBytesEncoder

from ejtp.address import *
from ejtp.identity.core import Identity, deserialize
from ejtp.identity.ref  import IdentRef

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

        >>> cache[['x', 'y', 'z']] = ident
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
            raise ValueError(
                'Trying to cache ident in the wrong location'
            )
        self.cache[location] = value

    def __delitem__(self, location):
        location = str_address(location)
        del self.cache[location]

    def update_ident(self, ident):
        self[str_address(ident.location)] = ident

    def update_idents(self, idents):
        for ident in idents:
            self.update_ident(ident)

    def filter_by_name(self, name):
        '''
        Return a new cache of every ident matching the given name.
        '''
        return [x for x in self.all() if x.name == name]

    def find_by_name(self, name):
        for ident in self.cache.values():
            if ident.name == name:
                return ident
        raise KeyError(name)

    def find_by_location(self, location):
        return self.cache[str_address(location)]

    def all(self):
        return self.cache.values()

    def ref(self, ident):
        if isinstance(ident, Identity):
            key = ident.key
        else:
            key = ident
        return IdentRef(key, self)

    def encrypt_capable(self):
        '''
        Return a list of every identity that can encrypt.
        '''
        return [i for i in self.all() if i.can_encrypt()]

    def sync(self, *caches):
        '''
        Sync to one or more other cache objects

        >>> from ejtp.tests.test_identity import mockup
        >>> cache1 = IdentityCache()
        >>> cache2 = IdentityCache()
        >>> cache1.update_ident(mockup("mitzi"))
        >>> cache1.sync(cache2)
        >>> cache2.find_by_name("mitzi@lackadaisy.com").location
        ['local', None, 'mitzi']
        '''
        sync_caches(self, *caches)

    def deserialize(self, cache_dict):
        '''
        Deserialize IdentityCache from straddr-keyed dict.

        >>> from ejtp.tests.test_identity import mockup
        >>> orig_cache = IdentityCache()
        >>> orig_cache.update_ident(mockup("mitzi"))

        >>> serialization = orig_cache.serialize()
        >>> new_cache = IdentityCache()
        >>> new_cache.deserialize(serialization)

        >>> new_cache.find_by_name("mitzi@lackadaisy.com").location
        ['local', None, 'mitzi']
        '''
        for straddr in cache_dict:
            ident = deserialize(cache_dict[straddr])
            if str_address(ident.location) != str_address(straddr):
                raise ValueError(   "Bad location key %r for %r", 
                                    straddr,
                                    ident.location)
            self.update_ident(ident)

    def serialize(self):
        '''
        Serialize IdentityCache to straddr-keyed dict.
        '''
        result = {}
        for straddr in self.cache:
            result[straddr.export()] = self.cache[straddr].serialize()
        return result

    @StringDecorator()
    def load_from(self, file_path = None, file_object = None):
        '''
        Load data from a serialization file.

        >>> cache = IdentityCache()
        >>> cache.load_from("resources/examplecache.json")
        >>> cache.find_by_name("atlas@lackadaisy.com").location
        '''
        if not file_object:
            if file_path:
                if isinstance(file_path, String):
                    file_path = file_path.export()
                file_object = open(file_path, 'r')
        if not file_object:
            raise ValueError("Must provide either file_path or file_object")

        self.deserialize(json.load(file_object))

    @StringDecorator()
    def save_to(self, file_path = None, file_object = None, **kwargs):
        '''
        Save data to a serialization file.

        >>> cache = IdentityCache()
        >>> cache.update_ident(mockup("mitzi"))
        >>> cache.update_ident(mockup("atlas"))
        >>> cache.update_ident(mockup("victor"))
        cache.save_to('resources/examplecache.json', indent=4)
        '''
        if not file_object:
            if file_path:
                if isinstance(file_path, String):
                    file_path = file_path.export()
                file_object = open(file_path, 'w')
        if not file_object:
            raise ValueError("Must provide either file_path or file_object")

        json.dump(
            self.serialize(),
            file_object,
            default = JSONBytesEncoder,
            **kwargs
        )

    def __repr__(self):
        return "<IdentityCache %r>" % repr(self.cache)

def sync_caches(*caches):
    sync = {}
    for c in caches:
        sync.update(c.cache)
    for c in caches:
        c.cache.update(sync)
