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

class ForwardClient(Client):
    def __init__(self, serveraddr):
        self.serveraddr = serveraddr
        self._status = {}

	def rcv_callback(self, msg, client_obj):
        pass

    def ack(self, messageid):
        pass

    def retrieve(self, hashes=None):
        pass

    def get_status(self, callback=None):
        pass

    @property
    def status(self):
        return self._status
