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


'''
    UDPJack

    IPv6 UDP jack, currently programmed quick and dirty to serve forever.
'''

import socket
import logging
logger = logging.getLogger(__name__)

from persei import RawDataDecorator

from ejtp.jacks import core as jack

class UDPJack(jack.Jack):

    def __init__(self, router, host='::', port=3972, ipv=6):
        if ipv==6:
            ifacetype = "udp"
            self.address = (host, port, 0, 0)
            sockfamily = socket.AF_INET6
        else: 
            ifacetype = "udp4"
            self.address = (host, port)
            sockfamily = socket.AF_INET

        jack.Jack.__init__(self, router, (ifacetype, (host, port)))
        self.sock = socket.socket(sockfamily, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
        self.closed = True
        self.lock_init.release()

    def route(self, msg):
        # Send frame to somewhere
        with self.lock_ready: pass # Make sure socket is ready
        address = msg.address
        location = address[1]
        if self.ifacetype == 'udp':
            address = (location[0], location[1], 0,0)
        else:
            address = (location[0], location[1])
        msg = msg.content
        sent = self.sock.sendto(msg.export(), address)
        logger.info("%d / %d %r -> %r", 
            sent, 
            len(msg), 
            self.address,
            address,
        )

    def run(self):
        with self.lock_init: pass # Make sure init is done, and ready to run
        self.closed = False
        self.lock_ready.release()
        while not self.closed:
            data = self.sock.recv(4096)
            self.recv(data)

    def close(self):
        self.closed = True
        self.lock_close.release()
