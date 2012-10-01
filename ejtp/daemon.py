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
from ejtp.util.hasher import strict
import re

errorcodes = {
    300:"Not authorized (Your client is not the controller)",
    301:"Not authorized (This path is filtered)",
    400:"Malformed content (Could not parse JSON)",
    401:"Malformed content (JSON data was not a {})",
    402:"Malformed content (No type argument given)",
    403:"Malformed content (Unrecognized command)",
    404:"Malformed content (Missing required argument)",
    500:"Command error (Could not import module)",
    501:"Command error (Class not found in module)",
    502:"Command error (Class initialization error)",
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

    def get_args(self, data, *args):
        result = []
        for name in args:
            if name in data:
                result.append(data[name])
            else:
                self.error(self.controller, 404, name)
                raise KeyError(name)
        return tuple(result)

    def client_init(self, data):
        logger.info("Initializing client...")

        # Unpack data from remote
        modname, classname, args, kwargs = (None,)*4
        try:
            modname,    classname, args,  kwargs = self.get_args(data, 
                'module', 'class','args','kwargs')
        except KeyError:
            return # Error already handled

        # Import module
        client_module, client_class = None, None
        try:
            client_module = __import__(modname, fromlist=[''])
        except ImportError:
            return self.error(self.controller, 500, data)

        # Get class object
        try:
            client_class = getattr(client_module, classname)
        except:
            return self.error(self.controller, 501, data)

        # Create class instance
        client = None
        try:
            client = client_class(self.router, *args, **kwargs)
        except:
            return self.error(self.controller, 502, data)

        self.success(data)

    def client_destroy(self, data):
        logger.info("Destroying client %s", strict(data))

    def success(self, data):
        logger.info("SUCCESFUL COMMAND %s", strict(data))
        self.write_json(self.controller, {
            'type':'ejtpd-success',
            'command': data,
        })

    def error(self, target, code, details=None):
        msg = errorcodes[code]
        logger.error("CLIENT ERROR #%d %s %r", code, msg, details or "")
        self.write_json(target, {
            'type':'ejtpd-error',
            'code': code,
            'msg':  msg,
            'details': details,
        })

class ControllerClient(Client):
    def __init__(self, router, interface, target, encryptor_cache = None, make_jack = True):
        Client.__init__(self, router, interface, encryptor_cache, make_jack)
        self.target = target

    def client_init(self, module, classname, *args, **kwargs):
        self.transmit('ejtpd-client-init', {
            'module':module,
            'class': classname,
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
    >>> modname, classname, interface = "ejtp.client", "Client", ["local", None, "Exampley"]
    >>> control.client_init(modname, classname, interface)
    INFO:ejtp.daemon: Initializing client...
    INFO:ejtp.daemon: SUCCESFUL COMMAND {"args":[["local",null,"Exampley"]],"class":"Client","kwargs":{},"module":"ejtp.client","type":"ejtpd-client-init"}
    INFO:ejtp.client: Client ['local', None, 'c2'] recieved from [u'local', None, u'c1']: '{"command":{"args":[["local",null,"Exampley"]],"class":"Client","kwargs":{},"module":"ejtp.client","type":"ejtpd-client-init"},"type":"ejtpd-success"}'
    >>> daemon.router.client(interface) #doctest: +ELLIPSIS
    <ejtp.client.Client object at ...>
    >>> control.client_destroy(interface)
    INFO:ejtp.daemon: Destroying client {"interface":["local",null,"Exampley"],"type":"ejtpd-client-destroy"}
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
