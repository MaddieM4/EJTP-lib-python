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
import re

errorcodes = {
    300:"Not authorized (Your client is not the controller)",
    301:"Not authorized (This path is filtered)",
    400:"Malformed content (Could not parse JSON)",
    401:"Malformed content (No command argument given)",
    402:"Malformed content (Unrecognized command)",
}

class DaemonClient(Client):
    def __init__(self, router, interface, controller, filter='.*', encryptor_cache = None, make_jack = True):
        Client.__init__(self, router, interface, encryptor_cache, make_jack)
        self.controller = controller
        self.set_filter(filter)

    def set_filter(self, filter_text):
        self.filter = re.compile(filter_text)

    def rcv_callback(self, msg, client_obj):
        sender = msg.addr
        if sender != self.controller:
            # Not the controller, reject it
            return self.error(sender, 300)
        data = None
        try:
            data = msg.jsoncontent
        except:
            return self.error(sender,400)
        if not "command" in data:
            return self.error(sender,401)
        command = data["command"]
        if   command == "init":
            self.client_init(data)
        elif command == "destroy":
            self.client_destroy(data)
        else:
            return self.error(sender,402,command)

    def client_init(self, data):
        print "Initializing client"

    def client_destroy(self, data):
        print "Destroying client"

    def error(self, target, code, details=None):
        self.write_json(target, {
            'code': code,
            'msg':  errorcodes[code],
            'details': details,
        })
