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

This module contains mock-ups for the new jack system. It is not intended
to be ever used in a release.
'''

from ejtp.jacks import connect, listen, register_jack
from ejtp.jacks.base import ReaderJack, WriterJack


# just some addresses
addr = ['myproto', ('example.com', 80)]


## Here come my ideas for using connections
# PROCESS 1
listen_conn = listen(local_addr)
client_conn, callsign = listen_conn.accept()
client_conn.send('Welcome, {0}!'.format(callsign), callsign)
client_conn.recv() # ('Hi my name is Peter!', 'Peter')
                   # it's supposed to be something like (msg, callsign)
client_conn.close() # sends some notification to PROCESS 2
listen_conn.close()

# PROCESS 2
conn = connect(addr)
conn.send('Hi, my name is Peter!', 'Peter') # 'Peter' is supposed to be the callsign
conn.recv() # ('Welcome, Peter!', 'Peter')
            # again, (msg, callsgin) here
conn.close() # don't necessarily need this here, because it gets closed in PROCESS 1

# now we could either have the connection class handle multiple connections the the
# same address. (i.e. connect() with the same address will return the same instance)
# or let the router do this.


## and here is how the Jacks should work
@register_jack('myproto')
class MyProtoReaderJack(ReaderJack):
    def create_connection(self, addr):
        pass


@register_jack('myproto')
class MyProtoWriterJack(WriterJack):
    def create_connection(self, addr):
        pass

# the create_connection methods will be called in connect() or listen()
# maybe names like ConnectorJack and ReaderJack may be more appropriate.
# Also, each jack implementation must implement a Connection subclass.
# The idea is, that Jacks provide basic functionality for the protocol
# like checking for availability in the os (e.g. check for ipv6) or load
# a list of channels for an IRC jack.
# Connections however do all the sending and receiving stuff.
