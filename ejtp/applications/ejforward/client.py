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

from persei import RawData

from ejtp.client import Client
from ejtp import frame
from ejtp.util.hasher import make as hashfunc

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
        data = msg.unpack()
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
                self.send(frame.createFrame(internal)) # forward to router
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
        '''
        data['type'] = dtype
        self.write_json(self.serveraddr, data)

    @property
    def status(self):
        return self._status
