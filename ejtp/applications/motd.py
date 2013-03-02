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

from ejtp.client import Client
from ejtp.address import *

class MOTDServer(Client):
    def __init__(self, router, interface, filename, message="", encryptor_cache=None, make_jack=True):
        Client.__init__(self, router, interface, encryptor_cache, make_jack)
        self.filename = filename
        self.message  = message

    def rcv_callback(self, msg, client_obj):
        sender = msg.sender
        response = None
        try:
            with open(self.filename) as rfile:
                response = rfile.read()
        except:
            response = self.message
        self.write_json(sender, {
            'type':'motd-response',
            'content': response,
        })

class MOTDClient(Client):
    def __init__(self, *args, **kwargs):
        Client.__init__(self, *args, **kwargs)
        self.callbacks = {}

    def request(self, remote, callback):
        '''
        Callbacks get called with arguments (frame msg, Client client)
        '''
        self.callbacks[str_address(remote)] = callback
        self.write_json(py_address(remote), {
            'type':'motd-request'
        })

    def rcv_callback(self, msg, client_obj):
        sender = msg.sender
        strsender = str_address(sender)
        if strsender not in self.callbacks:
            logger.info("Message from stranger: %r" % sender)
        self.callbacks[strsender](msg, self)
