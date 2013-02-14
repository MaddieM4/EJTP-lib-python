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

import os
from ejtp.util.compat import unittest, json

import ejtp.crypto
from ejtp.crypto.rotate import RotateEncryptor
from ejtp import testing # TODO: move it to tests
from ejtp.identity import Identity, IdentityCache
from ejtp.identity.core import deserialize
from ejtp.util.py2and3 import JSONBytesEncoder

class TestIdentity(unittest.TestCase):

    def setUp(self):
        self.ident = Identity('joe', ['rotate', 8], None)

    def test_name(self):
        self.assertEqual('joe', self.ident.name)

    def test_encryptor(self):
        self.assertIsInstance(self.ident.encryptor, RotateEncryptor)

    def test_encryptor_cache(self):
        e = self.ident.encryptor
        self.assertEqual(e, self.ident.encryptor)

    def test_signature(self):
        plaintext = 'example'
        sig = self.ident.sign(plaintext)
        self.assertTrue(self.ident.verify_signature(sig, plaintext))

    def test_public(self):
        ident = testing.identity()
        proto = ident.encryptor.proto()
        self.assertIn('PRIVATE', str(proto[1]))
        self.assertNotIn('PUBLIC', str(proto[1]))

        public_ident = ident.public()
        public_proto = public_ident.encryptor.proto()
        self.assertNotIn('PRIVATE', str(public_proto[1]))
        self.assertIn('PUBLIC', str(public_proto[1]))


class TestIdentitySerialize(unittest.TestCase):

    def setUp(self):
        self.ident = testing.identity()
        self.json_ident = json.dumps(self.ident.serialize(),
            default=JSONBytesEncoder)
        self.loaded_ident = json.loads(self.json_ident)

    def test_name(self):
        self.assertEqual('mitzi@lackadaisy.com', self.loaded_ident['name'])

    def test_encryptor_type(self):
        self.assertEqual('rsa', self.loaded_ident['encryptor'][0])

    def test_encryptor_has_key(self):
        self.assertEqual(2, len(self.loaded_ident['encryptor']))

    def test_location(self):
        self.assertEqual(['local', None, 'mitzi'], self.loaded_ident['location'])


class TestIdentityDeserialize(unittest.TestCase):

    def _assertMissingProperty(self, prop, data):
        self.assertRaisesRegexp(ValueError, "Missing ident property: '%s'" % prop, deserialize, data)

    def test_empty_dict(self):
        self._assertMissingProperty('name', {})

    def test_without_location(self):
        self._assertMissingProperty('location', {'name': 'Calvin'})

    def test_without_encryptor(self):
        self._assertMissingProperty('encryptor',
            {'name': 'Calvin', 'location': ["local", None, "calvin-freckle-mcmurray"]})

    def test_deserialize(self):
        data = {
            'name': 'Calvin',
            'location': ["local", None, "calvin-freckle-mcmurray"],
            'encryptor': ['rotate', 4],
            'comment': "Lives dangerously under Rocky's \"guidance.\""
        }
        ident = deserialize(data)
        self.assertEqual(data['name'], ident.name)
        self.assertEqual(data['location'], ident.location)
        self.assertIsInstance(ident.encryptor, RotateEncryptor)
        self.assertEqual(data['comment'], ident['comment'])


class TestIdentityCache(unittest.TestCase):

    def setUp(self):
        self.cache = IdentityCache()
        self.joe_ident = Identity('joe', ['rotate', 3], ['local', None, 'joe'])
        self.mitzi_ident = testing.identity('mitzi')
        self.atlas_ident = testing.identity('atlas')
        self.victor_ident = testing.identity('victor')

    def test_setitem_wrong_type(self):
        self.assertRaisesRegexp(TypeError, "Expected ejtp.identity.core.Identity",
            self.cache.__setitem__, self.joe_ident, [])

    def test_setitem_wrong_location(self):
        self.assertRaisesRegexp(ValueError, "Trying to cache ident in the wrong location",
            self.cache.__setitem__, ['x', 'y', 'z'], self.joe_ident)

    def test_serialize(self):
        self.cache.update_ident(self.mitzi_ident)
        serialized_ident = self.cache.serialize()
        self.assertIn('["local",null,"mitzi"]', serialized_ident)

    def test_encrypt_capable(self):
        self.cache.update_ident(self.mitzi_ident)
        self.cache.update_ident(self.atlas_ident.public())
        self.cache.update_ident(self.joe_ident)

        capable = [ident.name for ident in self.cache.encrypt_capable()]
        self.assertIn('joe', capable)
        self.assertIn('mitzi@lackadaisy.com', capable)
        self.assertNotIn('atlas@lackadaisy.com', capable)

    def _assert_caches(self, cache1, cache2):
        for item in zip(sorted(cache1.cache.keys()), sorted(cache2.cache.keys())):
            self.assertEqual(*item)

    def test_sync(self):
        mitzi_cache = IdentityCache()
        atlas_cache = IdentityCache()
        mitzi_cache.update_ident(self.mitzi_ident)
        atlas_cache.update_ident(self.atlas_ident)
        mitzi_cache.sync(atlas_cache)
        self._assert_caches(mitzi_cache, atlas_cache)

    def test_deserialize(self):
        self.cache.update_ident(self.mitzi_ident)
        self.cache.update_ident(self.atlas_ident)

        serialization = self.cache.serialize()
        new_cache = IdentityCache()
        new_cache.deserialize(serialization)
        self._assert_caches(self.cache, new_cache)

    def test_load_from_without_args(self):
        self.assertRaisesRegexp(ValueError, 'Must provide either file_path or file_object', self.cache.load_from)

    def test_load(self):
        self.cache.load_from('resources/examplecache.json')
        atlas_location = self.cache.find_by_name("atlas@lackadaisy.com").location
        self.assertListEqual(self.atlas_ident.location, atlas_location)

    def test_save_to_without_args(self):
        self.assertRaisesRegexp(ValueError, 'Must provide either file_path or file_object', self.cache.save_to)

    def test_save_to(self):
        self.cache.update_ident(self.mitzi_ident)
        self.cache.save_to('resources/temp.json', indent=4)
        os.remove('resources/temp.json')
