from ejtp.util.compat import unittest

from ejtp.tests.tools import TestCaseWithLog

class TestDaemon(TestCaseWithLog):

    def setUp(self):
        TestCaseWithLog.setUp(self)
        from ejtp.router import Router
        from ejtp.applications.daemon import DaemonClient, ControllerClient, logger
        router  = Router()
        ifaces = {
            'daemon': ['local', None, 'c1'],
            'control': ['local', None, 'c2'],
        }
        self.daemon = DaemonClient(router, ifaces['daemon'], ifaces['control'], make_jack = False)
        self.control = ControllerClient(router, ifaces['control'], ifaces['daemon'], make_jack = False)
        self.control.encryptor_cache = self.daemon.encryptor_cache
        self.daemon.encryptor_set(self.daemon.interface, ['rotate',  3])
        self.daemon.encryptor_set(self.control.interface, ['rotate', -7])

        self.listen(logger)

    def test_client_init_without_interface(self):
        self.control.client_init('ejtp.client', 'Client')
        self.assertInLog('INFO:ejtp.applications.daemon: Initializing client...')
        self.assertInLog('ERROR:ejtp.applications.daemon: __init__()')
        self.assertInLog('ERROR:ejtp.applications.daemon: CLIENT ERROR #502 Command error (Class initialization error)')
        self.assertInLog('ERROR:ejtp.applications.daemon: Remote error 502 Command error (Class initialization error)')

    def test_client_init_with_interface(self):
        self.control.client_init('ejtp.client', 'Client', ['local', None, 'Exampley'])
        self.assertInLog('INFO:ejtp.applications.daemon: Initializing client...')
        self.assertInLog('INFO:ejtp.applications.daemon: SUCCESFUL COMMAND')
        self.assertInLog('INFO:ejtp.applications.daemon: Remote client succesfully initialized (ejtp.client.Client, [["local",null,"Exampley"]], {})')

    def test_client_instance(self):
        from ejtp.client import Client
        interface = ['local', None, 'Exampley']
        self.control.client_init('ejtp.client', 'Client', interface)
        client = self.daemon.router.client(interface)
        self.assertIsInstance(client, Client)

    def test_client_destroy(self):
        interface = ['local', None, 'Exampley']
        self.control.client_init('ejtp.client', 'Client', interface)
        self.control.client_destroy(interface)
        self.assertInLog('INFO:ejtp.applications.daemon: Destroying client...')
        self.assertInLog('INFO:ejtp.applications.daemon: SUCCESFUL COMMAND {"interface":["local",null,"Exampley"],"type":"ejtpd-client-destroy"}')
        self.assertInLog('INFO:ejtp.applications.daemon: Remote client succesfully destroyed (["local",null,"Exampley"])')

        self.assertIsNone(self.daemon.router.client(interface))
