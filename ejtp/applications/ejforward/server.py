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

import logging
logger = logging.getLogger(__name__)

from persei import RawData, String

from ejtp.client import Client
from ejtp.address import *
from ejtp.util.hasher import make as hashfunc

class ForwardServer(Client):
    def __init__(self, router, interface, **kwargs):
        Client.__init__(self, router, interface, **kwargs)
        self.client_data = {}
        self.default_data = {
            'messages':{},
            'chopping_block':[],
            'status':{
                'total_count': 1000,
                'total_space': 32*1024, # 32kb of space default
                'used_count' : 0,
                'used_space' : 0,
            },
        }

    def relay(self, msg):
        '''
        To send a message through EJForward, simply onion route through the 
        server, client, and destination, in that order.

        >>> from ejtp.client import Client
        >>> client, server = test_setup()
        >>> dest   = Client(client.router, ['local', None, 'destination'])
        >>> sender = Client(client.router, ['local', None, 'sender'])
        >>> client.encryptor_set(sender.interface, ['rotate', 23])
        >>> client.encryptor_set(dest.interface, ['aes', 'brazil'])
        >>> dest.encryptor_cache = sender.encryptor_cache = client.encryptor_cache

        >>> def rcv_callback(msg, client):
        ...     print(msg.unpack())
        >>> message = {'type':'example'}
        >>> dest.rcv_callback = rcv_callback
        >>> sender.owrite_json(
        ...     [server.interface, client.interface, dest.interface],
        ...     message
        ... ) # doctest: +ELLIPSIS
        {...'type': ...'example'}
        '''
        address = str_address(msg.address)
        if address in self.client_data:
            mhash = self.store_message(address, msg.content.export())
            self.message(address, mhash)
        else:
            self.send(msg)

    def rcv_callback(self, msg, client_obj):
        data   = msg.unpack()
        mtype  = data['type']
        target = msg.sender
        if mtype=='ejforward-get-status':
            self.notify(target)
        elif mtype=='ejforward-retrieve':
            client = self.client(target)
            hashes = data['hashes'] or list(client['messages'].keys())[:5]
            for mhash in hashes:
                self.message(target, mhash)
        elif mtype=='ejforward-ack':
            hashes = data['hashes']
            for mhash in hashes:
                self.delete_message(target, mhash)
        else:
            logger.warning("Unknown message type, %r" % mtype)

    def notify(self, target):
        client = self.client(target)
        status = client['status']
        status['type'] = 'ejforward-notify'
        status['hashes'] = list(client['messages'].keys())[:5]
        self.write_json(
            target,
            status,
        )

    def message(self, target, mhash):
        self.write_json(
            target,
            {
                'type':'ejforward-message',
                'target':target,
                'data':RawData(self.client(target)['messages'][String(mhash)])
            },
        )

    def store_message(self, target, content):
        mhash = hashfunc(content)
        client = self.client(target)

        client['messages'][mhash] = content
        client['chopping_block'].append(mhash)
        client['status']['used_count'] += 1
        client['status']['used_space'] += len(content)
        self.trim(target)
        return mhash

    def delete_message(self, target, chophash):
        chophash = String(chophash)
        client = self.client(target)
        client['chopping_block'].remove(chophash)
        chopsize = len(client['messages'][chophash])
        del client['messages'][chophash]
        client['status']['used_count'] -= 1
        client['status']['used_space'] -= chopsize

    def trim(self, target):
        client = self.client(target)
        while (
                client['status']['used_count'] > client['status']['total_count']
            or  client['status']['used_space'] > client['status']['total_space']
              ):
            self.delete_message(target, client['chopping_block'][0])

    def client(self, address):
        '''
        Get client information for an interface address

        >>> server = ForwardServer(None, None, make_jack=False)
        >>> address = ['sad thoughts', 'lonely eyes']

        Trying to access client data not currently stored in database.

        >>> server.client(address)
        Traceback (most recent call last):
        KeyError: String('["sad thoughts","lonely eyes"]')

        Storing and accessing data.

        >>> server.create_client(address, {'hello':'world'})
        >>> server.client(address)
        {'hello': 'world'}

        Persistance/changing the data.

        >>> server.client(address)['sample'] = 'bacon'
        >>> server.client(address) == {'hello':'world', 'sample':'bacon'}
        True
        '''
        return self.client_data[str_address(address)]

    def create_client(self, address, data={}):
        address = str_address(address)
        self.client_data[address] = dict()
        self.client(address).update(data)

    def setup_client(self, address):
        '''
        Create a default-configured client.

        >>> server = ForwardServer(None, None, make_jack=False)
        >>> address = ['sad thoughts', 'lonely eyes']
        >>> server.setup_client(address)
        >>> from ejtp.util.hasher import strict
        >>> strict(server.client(address))
        String('{"chopping_block":[],"messages":{},"status":{"total_count":1000,"total_space":32768,"used_count":0,"used_space":0}}')
        '''
        self.create_client(address, self.default_data)


_demo_client_addr = ['local', None, 'client']
_demo_server_addr = ['local', None, 'server']

def test_setup():
    # Set up the demo client stuff in this module for further testing
    from ejtp.applications.ejforward.client import ForwardClient
    from ejtp.router import Router
    r = Router()
    client = ForwardClient(r, _demo_client_addr, _demo_server_addr)
    server = ForwardServer(r, _demo_server_addr)
    client.encryptor_set(_demo_client_addr, ['rotate', 5])
    client.encryptor_set(_demo_server_addr, ['rotate', 3])
    server.encryptor_cache = client.encryptor_cache
    server.setup_client(client.interface)
    return (client, server)

