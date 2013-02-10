import json

from ejtp.util.compat import unittest

import ejtp.crypto
from ejtp.crypto.rotate import RotateEncryptor
from ejtp import testing # TODO: move it to tests
from ejtp.identity import Identity
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
