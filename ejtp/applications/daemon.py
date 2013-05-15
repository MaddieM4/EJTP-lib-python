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

import re
import logging
logger = logging.getLogger(__name__)

from persei import String

from ejtp.client import Client
from ejtp.util.hasher import strict
from ejtp.address import *

errorcodes = {
    100:"Internal error (Reason unknown or unspecified)",
    300:"Not authorized (Your client is not the controller)",
    301:"Not authorized (This path is filtered)",
    302:"Not authorized (Your client is not the daemon)",
    400:"Malformed content (Could not parse JSON)",
    401:"Malformed content (JSON data was not a {})",
    402:"Malformed content (No type argument given)",
    403:"Malformed content (Unrecognized command)",
    404:"Malformed content (Missing required argument)",
    500:"Command error (Could not import module)",
    501:"Command error (Class not found in module)",
    502:"Command error (Class initialization error)",
    503:"Command error (Could not find client with that interface)",
}

class DaemonClient(Client):
    def __init__(self, router, interface, controller, filter='.*', encryptor_cache = None, make_jack = True):
        Client.__init__(self, router, interface, encryptor_cache, make_jack)
        self.controller = py_address(controller)
        self.set_filter(filter)

    def set_filter(self, filter_text):
        self.filter = re.compile(filter_text)

    def rcv_callback(self, msg, client_obj):
        sender = msg.sender
        if sender != self.controller:
            # Not the controller, reject it
            return self.error(sender, 300, {'controller':self.controller, 'sender':sender})
        data = None
        try:
            data = msg.unpack()
        except:
            return self.error(sender,400)
        if not isinstance(data, dict):
            return self.error(sender,401)
        if not "type" in data:
            return self.error(sender,402)
        mtype = data["type"]
        try:
            if   mtype == "ejtpd-client-init":
                self.client_init(data)
            elif mtype == "ejtpd-client-destroy":
                self.client_destroy(data)
            else:
                return self.error(sender,403,command)
        except Exception as e:
            logger.error(e)
            return self.error(sender, 100, data)

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
        except Exception as e:
            logger.error(e)
            data['exception'] = repr(e)
            return self.error(self.controller, 502, data)

        self.success(data)

    def client_destroy(self, data):
        logger.info("Destroying client...")

        # Unpack data from remote
        interface = None
        try:
            interface = self.get_args(data, 'interface')[0]
        except KeyError:
            return # Error already handled

        # Find and destroy client holding that interface
        if self.router.client(interface) != None:
            self.router.kill_client(interface)
        else:
            return self.error(self.controller, 503, data)

        self.success(data)

    def success(self, data):
        logger.info("SUCCESFUL COMMAND %s", strict(data).export())
        self.write_json(self.controller, {
            'type':'ejtpd-success',
            'command': data,
        })

    def error(self, target, code, details=None):
        msg = errorcodes[code]
        logger.error("CLIENT ERROR #%d %s %s", code, msg, (details and strict(details) or String()).export())
        self.write_json(target, {
            'type':'ejtpd-error',
            'code': code,
            'msg':  msg,
            'details': details,
        })

class ControllerClient(Client):
    def __init__(self, router, interface, target, encryptor_cache = None, make_jack = True):
        Client.__init__(self, router, interface, encryptor_cache, make_jack)
        self.target = py_address(target)

    def rcv_callback(self, msg, client_obj):
        sender = msg.sender
        if sender != self.target:
            # Not the daemon, drop it
            return
        data = None
        try:
            data = msg.unpack()
        except:
            return self.error(sender,400)
        if not isinstance(data, dict):
            return self.error(sender,401)
        if not "type" in data:
            return self.error(sender,402)
        mtype = data["type"]
        try:
            if   mtype == "ejtpd-success":
                self.success(data)
            elif mtype == "ejtpd-error":
                logger.error("Remote error %d %s %s", data['code'], data['msg'], strict(data['details']).export())
                self.response_callback(False, data)
            else:
                return self.error(sender,403,command)
        except Exception as e:
            logger.error(e)
            return self.error(sender, 100, data)

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

    def response_callback(self, success, data):
        pass

    def success(self, data):
        if 'command' in data:
            command = data['command']
            command_type = None
            if 'type' in command:
                command_type = command['type']

            if   command_type == 'ejtpd-client-init':
                modname   = ("module" in command and command["module"]) or ''
                classname = ("class"  in command and command["class"])  or ''
                args      = ("args"   in command and command["args"])   or []
                kwargs    = ("kwargs" in command and command["kwargs"]) or {}
                logger.info("Remote client succesfully initialized (%s.%s, %s, %s)", modname, classname, strict(args).export(), strict(kwargs).export())
            elif command_type == 'ejtpd-client-destroy':
                interface = ("interface" in command and command["interface"]) or ''
                logger.info("Remote client succesfully destroyed (%s)", strict(interface).export())
            else:
                logger.info("Remote command succesful (Unrecognized command - %r)", command)
        else:
            logger.info("Remote command succesful (daemon did not report details)")
        self.response_callback(True, data)

    def error(self, target, code, details=None):
        self.transmit("ejtpd-error", {
            'code': code,
            'msg':  errorcodes[code],
            'details': details,
        })
