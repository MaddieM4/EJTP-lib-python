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

from ejtp.client import Client
from ejtp.address import *

class ForwardServer(Client):
    def __init__(self, router, interface, **kwargs):
        Client.__init__(self, router, interface, **kwargs)
        self.client_data = {}
        self.default_data = {
            'messages':{},
            'chopping_block':[],
            'prefix':'',
            'status':{
                'total_count': 1000,
                'total_space': 32*1024, # 32kb of space default
                'used_count' : 0,
                'used_space' : 0,
            },
        }

    def rcv_callback(self, msg, client_obj):
        data   = msg.jsoncontent
        mtype  = data['type']
        target = msg.addr
        if mtype=='ejforward-get-status':
            self.notify(target)
        else:
            print "Unknown message type, %r" % mtype

    def notify(self, target):
        # TODO : Test me
        client = self.client(target)
        status = client['status']
        status['type'] = 'ejforward-notify'
        status['hashes'] = client['messages'].keys()[:5]
        self.write_json(
            target,
            status,
        )

    def message(self, target, messageid):
        # TODO : Test me
        pass

    def client(self, address):
        '''
        Get client information for an interface address

        >>> server = ForwardServer(None, None, make_jack=False)
        >>> address = ['sad thoughts', 'lonely eyes']

        Trying to access client data not currently stored in database.

        >>> server.client(address)
        Traceback (most recent call last):
        KeyError: '["sad thoughts","lonely eyes"]'

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
        '{"chopping_block":[],"messages":{},"prefix":"","status":{"total_count":1000,"total_space":32768,"used_count":0,"used_space":0}}'
        '''
        self.create_client(address, self.default_data)
