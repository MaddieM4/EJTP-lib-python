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
import json

from persei import JSONBytesEncoder, String

from ejtp.util.compat import unittest
from ejtp.tests.resource_path import testing_path
import ejtp.crypto
from ejtp.crypto.rotate import RotateEncryptor
from ejtp.identity import Identity, IdentityCache, IdentRef
from ejtp.identity.core import deserialize

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
        ident = mockup()
        proto = ident.encryptor.proto()
        self.assertIn('PRIVATE', str(proto[1]))
        self.assertNotIn('PUBLIC', str(proto[1]))

        public_ident = ident.public()
        public_proto = public_ident.encryptor.proto()
        self.assertNotIn('PRIVATE', str(public_proto[1]))
        self.assertIn('PUBLIC', str(public_proto[1]))

    def test_equality(self):
        self.assertTrue(self.ident == Identity('joe', ['rotate', 8], None))
        self.assertFalse(self.ident == Identity('joke', ['rotate', 8], None))
        self.assertFalse(self.ident == Identity('joe', ['rotate', 9], None))
        self.assertFalse(self.ident == Identity('joe', ['rotate', 8], "tangerine"))
        self.assertFalse(self.ident == Identity('joe', ['rotate', 8], None, arbitrary="hula"))

    def test_key(self):
        # Location is None
        self.assertRaises(TypeError, lambda: self.ident.key)

        # Set location to legitimate data
        self.ident.location = ['local', None, 'joey']
        self.assertEqual(self.ident.key, String('["local",null,"joey"]'))

class TestIdentitySerialize(unittest.TestCase):

    def setUp(self):
        self.ident = mockup()
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
        self.mitzi_ident = mockup('mitzi')
        self.atlas_ident = mockup('atlas')
        self.victor_ident = mockup('victor')

    def test_setitem_wrong_type(self):
        self.assertRaisesRegexp(TypeError, "Expected ejtp.identity.core.Identity",
            self.cache.__setitem__, self.joe_ident, [])

    def test_setitem_wrong_location(self):
        self.assertRaisesRegexp(ValueError, "Trying to cache ident in the wrong location",
            self.cache.__setitem__, ['x', 'y', 'z'], self.joe_ident)

    def test_update_idents(self):
        idents = [self.joe_ident, self.victor_ident]
        self.cache.update_idents(idents)
        self.assertEquals(
            sorted(self.cache.all(), key=lambda x:x.key),
            sorted(idents, key=lambda x:x.key)
        )
        for i in idents:
            self.assertEquals(self.cache[i.location], i)

    def test_filter_by_name(self):
        # Create alternate-universe Joe
        alt_joe = self.joe_ident.clone()
        alt_joe.location = ['local', None, 'alt_joe']

        idents = [self.mitzi_ident, self.joe_ident, alt_joe]
        self.cache.update_idents(idents)

        self.assertEqual(
            self.cache.filter_by_name(self.mitzi_ident.name),
            [self.mitzi_ident]
        )

        joe_filtered = self.cache.filter_by_name(self.joe_ident.name)
        self.assertEqual(
            sorted(joe_filtered, key=lambda x:x.key),
            sorted([self.joe_ident, alt_joe], key=lambda x:x.key)
        )

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
        self.cache.load_from(testing_path('examplecache.json'))
        atlas_location = self.cache.find_by_name("atlas@lackadaisy.com").location
        self.assertListEqual(self.atlas_ident.location, atlas_location)

    def test_save_to_without_args(self):
        self.assertRaisesRegexp(ValueError, 'Must provide either file_path or file_object', self.cache.save_to)

    def test_save_to(self):
        filename = 'temp.json'
        self.cache.update_ident(self.mitzi_ident)
        self.cache.save_to(filename, indent=4)
        os.remove(filename)

class TestIdentityRef(unittest.TestCase):

    def setUp(self):
        self.ident = mockup()
        self.cache = IdentityCache()
        self.cache.update_ident(self.ident)
        self.ref = IdentRef(self.ident.key, self.cache)

    def thorough_equality(self, other_ref):
        self.assertEqual(self.ref, other_ref)
        self.assertEqual(hash(self.ref), hash(other_ref))

    def thorough_inequality(self, ineq_ref):
        self.assertNotEqual(self.ref, ineq_ref)
        self.assertNotEqual(hash(self.ref), hash(ineq_ref))

    def test_eq(self):
        self.thorough_equality(IdentRef(self.ident.key, self.cache))
        self.thorough_inequality(IdentRef("random key", self.cache))
        self.thorough_inequality(IdentRef(self.ident.key, IdentityCache()))

    def test_deref(self):
        self.assertEqual(self.ident, self.ref.deref())

    def test_from_cache(self):
        self.assertEqual(self.ref, self.cache.ref(self.ident))
        self.assertEqual(self.ref, self.cache.ref(self.ident.key))

    def test_from_ident(self):
        self.assertEqual(self.ref, self.ident.ref(self.cache))

    def test_hashable(self):
        # What can I say, I'm paranoid.
        myset = set([self.ref])
        self.assertIn(self.ref, myset)
        self.assertEquals(list(myset), [self.ref])

mockups = {
    "mitzi":("mitzi@lackadaisy.com", ["rsa","-----BEGIN RSA PRIVATE KEY-----\nMIICXAIBAAKBgQDAZQNip0GPxFZsyxcgIgyvuPTHsruu66DBsESG5/Pfbcye3g4W\nwfg+dBP3IfUnLB4QXGzK42BAd57fCBXOtalSOkFoze/C2q74gYFBMvIPbEfef8yQ\n83uoNkYAFBVp6yNlT51IQ2mY19KpqoyxMZftxwdtImthE5UG1knZE64sIwIDAQAB\nAoGAIGjjyRqj0LQiWvFbU+5odLGTipBxTWYkDnzDDnbEfj7g2WJOvUavqtWjB16R\nDahA6ECpkwP6kuGTwb567fdsLkLApwwqAtpjcu96lJpbRC1nq1zZjwNB+ywssqfV\nV3R2/rgIEE6hsWS1wBHufJeqBZtlkeUp/VEx/uopyuR/WgECQQDJOaFSutj1q1dt\nNO23Q6w3Ie4uMQ59rWeRxXA5+KjDZCxrizzo/Bew5ZysJzHB2n8QQ15WJ7gTSjwJ\nMQdl/7SJAkEA9MQG/6JivkhUNh45xMYqnMHuutyIeGE17QndSfknU+8CX9UBLjsL\nw1QU+llJ3iYfMPEDaydn0HJ8+iinyyAISwJAe7Z2vEorwT5KTdXQoG92nZ66tKNs\naVAG8NQWH04FU7tuo9/C3uq+Ff/UxvKB4NDYdcM1aHqa7SEir/P4vHjtIQJAFKc9\n1/BB2MCNqoteYIZALj4HAOl+8nlxbXD5pTZK5UAzuRZmJRqCYZcEtiM2onIhC6Yq\nna4Tink+pnUrw24OhQJBAIjujQS5qwOf2p5yOqU3UYsBv7PS8IitmYFARTlcYh1G\nrmcIPHRtkxIwNuFxy3ZRRPEDGFa82id5QHUJT8sJbqY=\n-----END RSA PRIVATE KEY-----"], ['local', None, 'mitzi']),
    "atlas":("atlas@lackadaisy.com", ["rsa","-----BEGIN RSA PRIVATE KEY-----\nMIICXgIBAAKBgQCvCM8MTSOSeA8G62b9Fg2Ic18JoHoswqn7kmU+qmYxJnTd0rSS\nYaQWiSflchTBgGcbItR4jsktYifOSfp7Cl1k5IHXqGKLHtIt8Fo02k/ajR5DzGJN\n2yAJfbBCi43ifOaVKwjuJqcFKhuPUqNJecFn8m62QOQehrIlUAlnnM7OXQIDAQAB\nAoGBAJGrVRU5xZcKUAdENkv+5Hhg/AE5CzThNTJnXddPXQkepjhOOXVxyWvv7cIo\ntVltEWImFInY21jnzZUDQHDR6XLCe8B3LRlOWrkv7+byesIFkNH9C7uvheD5xxiG\nzPpOkpwcms3QW+/FmhN5Wia+4oeHB4J9uAjJmNoaddfqAhWBAkEAwdEjMzJaKIx5\n6OIyYAEnC6lvVI6Qx/ssKQH7GhaItxzLZRaIaK4XUgrL5q1OHNNCCFgREw7nhyu3\nZnt8v833rQJBAOcw/wQ0iQktluqKoT4i73hRkGk7MTB2Y/4e2YTVnypUtQC+jxs1\nND3CJj59oJojfA3SJg0M0pWXcMKIIhRxx3ECQQCVl6zafBeYSmxhsgx9iwYu+xSh\np/PZVmTMNeowRYo6AvB90nlwikYXnZupLMQofWnu9MIg+pT7AGPqpo8vn3J1AkAU\nowEAhRf+Y71m7jz6aO/rU4yKeCgp5UeDtYlBHDh69Ni7Wkc37IXfRWdYiKo/WA+I\nxEt1OsHJbJ06ICC6pnVhAkEAio1qXj8vLi9t9xocRe8LIthaYBslw4B8yY69fRhd\nuQifuvld7xjeXsfCWRmA4t72SmcAyzMaG5wnqhLNeCXXYw==\n-----END RSA PRIVATE KEY-----"], ['local', None, 'atlas']),
    "victor":("victor@lackadaisy.com", ["rsa","-----BEGIN RSA PRIVATE KEY-----\nMIICXAIBAAKBgQC6efOadLJZpX837OIpAlqO2NQEfOA1DE8lfC1q8fKGtMlEl8Oq\nR9lbEiMdsbg5M902Gi33UMlJuap+5TaGEBJDBJZNr3d2LFOjlEPGyJeqiu5PnBjX\n3vZx97y+NUm71rsL7k1KRjzAQnuCPSSqQdo5GLdNODgTa2ljXQ4Khd/9CwIDAQAB\nAoGARbSkfQ42RRB6N7uS5uV8WH1w86SCYxIQ2+BJUfrTP8uAmOVqPNLSyxpCii0O\nwkNC46BxoktOkwKWWwzvjrmfOU2hEga3ny/S1r2VU6nfex29ozl+gUD7zEkB8MaV\nQqnRF18gkeGvHcCMU5nSbjYaosp39yj9qBcRDePQIWN3aRECQQDCj8FWSyrP/zoN\n+6YR3j/0Ty6b43KDU3fcvG/+IvHhB+OFawiPlR3uPGYVJG0CfbWC/QEtx90VcGi5\nOnaQRtsXAkEA9VyYg5+5ZzfbfGqZZZRvPHk08rsquAXnGWkT67lobkBtWvx0TxYo\nTKi8PwLZ8paLA3wf2VDJ6/Ufn5APOtSWLQJAP5cUrcurlofoxaE2SijF5mfq5/CT\nAPFK/85nHDz3qYEWkAjHp4YpXjBHfSmGp4XGyaU/uWLVk6hF0iSVk9pUyQJACNya\nSY64RIkY7UpwVeHhjp6WEfo+lbzo1tsbtBTTN8At8u5RSRX0yKgDfIce1gsn5C1U\nfSXU1SfaR4oNcsOA1QJBAKDEQ4PATuH46E7e3Ie+A5AUVSyLqO5H2SC0yg6zduG6\npxbmsfpVLOfko+j9YrH+OdD5WIAjN/wL1CtmVhqSLr8=\n-----END RSA PRIVATE KEY-----"], ['local', None, 'victor']),
}

def mockup(name="mitzi"):
    return Identity(*mockups[name])
