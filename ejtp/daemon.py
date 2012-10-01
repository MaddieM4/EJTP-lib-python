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
from ejtp.util.hasher import strict
import re

errorcodes = {
    300:"Not authorized (Your client is not the controller)",
    301:"Not authorized (This path is filtered)",
    400:"Malformed content (Could not parse JSON)",
    401:"Malformed content (JSON data was not a {})",
    402:"Malformed content (No type argument given)",
    403:"Malformed content (Unrecognized command)",
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
        if type(data) != dict:
            return self.error(sender,401)
        if not "type" in data:
            return self.error(sender,402)
        mtype = data["type"]
        if   mtype == "ejtpd-client-init":
            self.client_init(data)
        elif mtype == "ejtpd-client-destroy":
            self.client_destroy(data)
        else:
            return self.error(sender,403,command)

    def client_init(self, data):
        print "Initializing client " + strict(data)

    def client_destroy(self, data):
        print "Destroying client " + strict(data)

    def error(self, target, code, details=None):
        self.write_json(target, {
            'type':'ejtpd-error',
            'code': code,
            'msg':  errorcodes[code],
            'details': details,
        })

class ControllerClient(Client):
    def __init__(self, router, interface, target, encryptor_cache = None, make_jack = True):
        Client.__init__(self, router, interface, encryptor_cache, make_jack)
        self.target = target

    def client_init(self, module, classname, *args, **kwargs):
        self.transmit('ejtpd-client-init', {
            'module':module,
            'classname': classname,
            'args': args,
            'kwargs':kwargs,
        })

    def client_destroy(self, interface):
        self.transmit('ejtpd-client-destroy', {
            'interface':interface,
        })

    def transmit(self, type, data={}):
        data['type'] = type
        self.write_json(self.target, data)

    def error(self, target, code, details=None):
        self.transmit("ejtpd-error", {
            'code': code,
            'msg':  errorcodes[code],
            'details': details,
        })

def mock_locals(name1='c1', name2='c2'):
    '''
    Returns two clients that talk locally through a router.
    >>> daemon, control = mock_locals()
    >>> modname, classname, interface = "mod", "class", ["local", None, "Exampley"]
    >>> control.client_init(modname, classname, interface)
    Initializing client {"args":[["local",null,"Exampley"]],"classname":"class","kwargs":{},"module":"mod","type":"ejtpd-client-init"}
    >>> control.client_destroy(interface)
    Destroying client {"interface":["local",null,"Exampley"],"type":"ejtpd-client-destroy"}
    '''
    from router import Router
    r  = Router()
    ifaces = {
        'daemon':  ['local', None, name1],
        'control': ['local', None, name2],
    }
    daemon  = DaemonClient(    r, ifaces['daemon'], ifaces['control'], make_jack = False)
    control = ControllerClient(r, ifaces['control'], ifaces['daemon'], make_jack = False)
    control.encryptor_cache = daemon.encryptor_cache
    daemon.encryptor_set(daemon.interface,  ['rotate',  3])
    daemon.encryptor_set(control.interface, ['rotate', -7])
    return (daemon, control)
