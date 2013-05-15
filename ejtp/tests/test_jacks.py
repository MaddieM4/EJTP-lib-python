from ejtp.util.compat import unittest

import threading

from persei import String, RawData

from ejtp import router, client
from ejtp.jacks.stream import Connection

class TestJacks(unittest.TestCase):

    def setUp(self):
        self.routerA = router.Router()
        self.routerB = router.Router()

    def test_udp4(self):
        self.make_test(
            ['udp4', ['127.0.0.1', 18999], 'charlie'],
            ['udp4', ['127.0.0.1', 19999], 'stacy'])

    def test_udp(self):
        self.make_test(
            ['udp', ['::1', 8999], 'charlie'],
            ['udp', ['::1', 9999], 'stacy'])

    def test_tcp4(self):
        self.make_test(
            ['tcp4', ['127.0.0.1', 18999], 'charlie'],
            ['tcp4', ['127.0.0.1', 19999], 'stacy'])

    def test_tcp(self):
        self.make_test(
            ['tcp', ['::1', 8999], 'charlie'],
            ['tcp', ['::1', 9999], 'stacy'])

    def make_test(self, ifaceA, ifaceB, messageAB='A => B', messageBA='B => A', timeout=0.5):
        clientA = client.Client(self.routerA, ifaceA)
        clientB = client.Client(self.routerB, ifaceB)
        self.assertNotEqual(clientA.router, clientB.router)

        # Share encryptor data
        clientA.encryptor_cache = clientB.encryptor_cache
        clientA.encryptor_set(ifaceA, ['rotate', 43])
        clientA.encryptor_set(ifaceB, ['rotate', 93])

        # Syncronize for output consistency
        transfer_condition = threading.Condition()

        received = []

        def rcv_callback(msg, client_obj):
            transfer_condition.acquire()
            received.append((client_obj.interface, msg.sender, msg.unpack()))
            transfer_condition.notifyAll()
            transfer_condition.release()
        clientA.rcv_callback = clientB.rcv_callback = rcv_callback

        # Wait for both jacks to be ready
        for r in (self.routerA, self.routerB):
            with list(r._jacks.values())[0].lock_ready: pass

        transfer_condition.acquire()
        clientA.write_json(ifaceB, messageAB)
        transfer_condition.wait(timeout)
        transfer_condition.release()

        transfer_condition.acquire()
        clientB.write_json(ifaceA, messageBA)
        transfer_condition.wait(timeout)
        transfer_condition.release()

        self.assertEqual((ifaceB, ifaceA, messageAB), received[0])
        self.assertEqual((ifaceA, ifaceB, messageBA), received[1])

    def tearDown(self):
        self.routerA.stop_all()
        self.routerB.stop_all()

class TestJackStream(unittest.TestCase):

    def setUp(self):
        self.connection = Connection()
        self.plaintext = "The pursuit of \x00 happiness"
        self.wrapped = self.connection.wrap(self.plaintext)

    def test_receive(self):
        self.connection.inject(self.wrapped)
        self.assertEqual(RawData(self.plaintext), self.connection.recv())

    def test_receive_partial(self):
        self.connection.inject(self.wrapped[:5])
        self.assertIsNone(self.connection.recv())

        self.connection.inject(self.wrapped[5:])
        self.assertEqual(RawData(self.plaintext), self.connection.recv())

