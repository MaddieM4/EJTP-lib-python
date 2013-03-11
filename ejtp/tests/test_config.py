import os
import os.path

from ejtp.util.compat import unittest
from ejtp import config

class TestConfig(unittest.TestCase):

    config_file = os.path.join(
        os.path.dirname(__file__),
        'examplecache.json'
    )

    def test_test_filenames(self):
        self.assertEqual([self.config_file],
            config.test_filenames([self.config_file, 'some/invalid/file.json']))

    def test_test_filenames_env_var(self):
        os.environ['SOME_PATH'] = self.config_file + ':another/invalid/file.json'
        self.assertEqual([self.config_file],
            config.test_filenames(['some/invalid/file.json'], env_var='SOME_PATH'))

    def test_configure_identity_cache(self):
        from ejtp.identity.cache import IdentityCache
        cache = IdentityCache()
        config.configure_identity_cache(cache, [self.config_file])
        self.assertEqual(['local', None, 'mitzi'],
            cache.find_by_name('mitzi@lackadaisy.com').location)

    def test_configure_ejtpd(self):
        self.assertRaises(NotImplementedError, config.configure_ejtpd, [])
