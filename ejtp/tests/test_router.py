from ejtp.util.compat import unittest
from ejtp import router

class TestRouter(unittest.TestCase):

    def setUp(self):
        self.router = router.Router()

    def test_jack_already_loaded(self):
        from ejtp.jacks import Jack
        class DummyJack(Jack):
            def run(self, *args):
                pass

        jack = DummyJack(self.router, (1, 2, 3))
        self.assertRaisesRegexp(ValueError,
            'jack already loaded', self.router._loadjack, jack)
