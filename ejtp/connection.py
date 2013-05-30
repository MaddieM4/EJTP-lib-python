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

# This file may be moved into the jacks package.

class Connection(object):
    def __init__(self, jack, addr_local, addr_remote):
        '''
        Class that abstracts a continuous connection to a remote address.

        Arguments:
        jack  : a BaseJack decendent instance
        local : local EJTP addr
        remote: remote EJTP addr
        '''
        self.jack   = jack
        self.local  = addr_local
        self.remote = addr_remote

    def send(self, data):
        '''
        Send a frame to a remote address.

        Arguments:
        data: frame to send.
        '''
        self.jack.send(self, data)

    def recv(self, data):
        '''
        Recieve frame from remote end.

        Arguments:
        data: frame to recieve.
        '''
        self.router.recv(data)

    def close(self):
        '''
        Close all sockets and de-register from Jack.
        '''
        self.router.unload_connection(self)
        self.jack.close_connection(self)

    @property
    def router(self):
        return self.jack.router
