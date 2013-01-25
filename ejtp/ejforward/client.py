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

from ejtp import logging
logger = logging.getLogger(__name__)

from ejtp.client import Client
from ejtp import frame
from ejtp.util.hasher import make as hashfunc
from ejtp.util.py2and3 import RawData

_demo_client_addr = ['local', None, 'client']
_demo_server_addr = ['local', None, 'server']

class ForwardClient(Client):
    def __init__(self, router, interface, serveraddr, **kwargs):
        '''
        Client side for EJForward protocol. Takes server address as constructor arg.
        '''
        Client.__init__(self, router, interface, **kwargs)
        self.serveraddr = serveraddr
        self._status = {}
        self._status_callbacks = []

    def rcv_callback(self, msg, client_obj):
        data = msg.jsoncontent
        mtype = data['type']
        if mtype=='ejforward-notify':
            self._status = data
            for callback in self._status_callbacks:
                callback(self)
            self._status_callbacks = []
        elif mtype=='ejforward-message':
            internal = RawData(data['data'])
            self.ack([hashfunc(internal)])
            try:
                self.send(frame.Frame(internal)) # forward to router
            except ValueError:
                logger.warning("Invalid frame, discarding")
        else:
            logger.warning("Unknown message type, %r" % mtype)

    def ack(self, hashes):
        self.upload(
            'ejforward-ack',
            {
                'hashes': list(hashes),
            },
        )

    def retrieve(self, hashes=None):
        '''
        Get the current status according to the server.

        >>> from ejtp.util.hasher import strict
        >>> client, server = test_setup()
        >>> def on_status(client):
        ...     print("Status is: " + strict(client.status).export())
        >>> client.get_status(on_status)
        Status is: {"hashes":[],"total_count":1000,"total_space":32768,"type":"ejforward-notify","used_count":0,"used_space":0}

        >>> len("fakey message")
        13
        >>> mhash = server.store_message(client.interface, "fakey message")
        >>> server.client(client.interface)['messages']
        {String('4fc5bbbfefe38b84b935fee015c192e397b6eac3'): 'fakey message'}
        >>> client.get_status(on_status)
        Status is: {"hashes":["4fc5bbbfefe38b84b935fee015c192e397b6eac3"],"total_count":1000,"total_space":32768,"type":"ejforward-notify","used_count":1,"used_space":13}

        >>> client.retrieve(hashes=[mhash])
        WARNING:ejtp.ejforward.client: Invalid frame, discarding
        >>> server.client(client.interface)['messages']
        {}
        >>> client.get_status(on_status)
        Status is: {"hashes":[],"total_count":1000,"total_space":32768,"type":"ejforward-notify","used_count":0,"used_space":0}
        '''
        self.upload(
            'ejforward-retrieve',
            {
                'hashes': list(hashes),
            },
        )

    def get_status(self, callback=None):
        '''
        Get the current status according to the server.

        >>> from ejtp.util.hasher import strict
        >>> client, server = test_setup()
        >>> def on_status(client):
        ...     print("Status is: " + strict(client.status).export())
        >>> client.get_status(on_status)
        Status is: {"hashes":[],"total_count":1000,"total_space":32768,"type":"ejforward-notify","used_count":0,"used_space":0}
        '''
        if callback:
            self._status_callbacks.append(callback)
        self.upload(
            'ejforward-get-status',
            {},
        )

    def upload(self, dtype, data):
        '''
        Send a message to the server.

        >>> client, server = test_setup()
        >>> client.upload("farfagnugen", {}) # doctest: +ELLIPSIS 
        WARNING:ejtp.ejforward.server: Unknown message type, ...'farfagnugen'
        '''
        data['type'] = dtype
        self.write_json(self.serveraddr, data)

    @property
    def status(self):
        return self._status

def test_setup():
    # Set up the demo client stuff in this module for further testing
    from ejtp.ejforward.server import ForwardServer
    from ejtp.router import Router
    r = Router()
    client = ForwardClient(r, _demo_client_addr, _demo_server_addr)
    server = ForwardServer(r, _demo_server_addr)
    client.encryptor_set(_demo_client_addr, ['rotate', 5])
    client.encryptor_set(_demo_server_addr, ['rotate', 3])
    server.encryptor_cache = client.encryptor_cache
    server.setup_client(client.interface)
    return (client, server)

