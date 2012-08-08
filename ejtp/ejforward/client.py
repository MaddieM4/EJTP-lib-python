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
from ejtp import frame

class ForwardClient(Client):
    def __init__(self, serveraddr):
        # TODO : Test me
        self.serveraddr = serveraddr
        self._status = {}
        self._status_callbacks = []

    def rcv_callback(self, msg, client_obj):
        # TODO : Test me
        data = msg.jsoncontent
        mtype = data['type']
        if mtype=='ejforward-notify':
            self._status = data
            for callback in self._status_callbacks:
                callback(self)
            self._status_callbacks = []
        elif mtype=='ejforward-message':
            internal = data['data']
            self.send(frame(internal)) # forward to router
        else:
            print "Unknown message type, %r" % mtype

    def ack(self, hashes):
        # TODO : Test me
        self.upload(
            'ejforward-ack',
            {
                'hashes': list(hashes),
            },
        )

    def retrieve(self, hashes=None):
        # TODO : Test me
        self.upload(
            'ejforward-retrieve',
            {
                'hashes': list(hashes),
            },
        )

    def get_status(self, callback=None):
        # TODO : Test me
        if callback:
            self._status_callbacks.append(callback)
        self.upload(
            'ejforward-get-status',
            {},
        )

    def upload(self, dtype, data):
        # TODO : Test me
        '''
        Send a message to the server.
        '''
        data['type'] = dtype
        self.write_json(self.serveraddr, data)

    @property
    def status(self):
        # TODO : Test me
        return self._status
