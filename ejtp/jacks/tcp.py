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

import socket
import logging
logger = logging.getLogger(__name__)

from persei import RawDataDecorator

from ejtp.jacks import stream

class TCPJack(stream.StreamJack):

    def __init__(self, router, host='::', port=3972, ipv=6):
        if ipv==6:
            ifacetype = "tcp"
            self.address = (host, port, 0, 0)
            self.sockfamily = socket.AF_INET6
        else: 
            ifacetype = "tcp4"
            self.address = (host, port)
            self.sockfamily = socket.AF_INET

        stream.StreamJack.__init__(self, router, (ifacetype, (host, port)))
        self.closed = True
        self.lock_init.release()

    def run(self):
        with self.lock_init: pass # Make sure init is done, and ready to run
        self.server = socket.socket(self.sockfamily, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.address)
        self.lock_ready.release()
        self.server.listen(5)
        self.closed = False
        try:
            while not self.closed:
                try:
                    conn, addr = self.server.accept()
                    interface = [self.interface[0], addr[:2]]
                    self.add_connection(interface, 
                        TCPConnection(self, interface, connection=conn)
                    )
                except socket.error:
                    pass
            for conn in list(self.connections.values()):
                conn.close()
        finally:
            self.lock_close.release()


    def close(self):
        kill_socket(self.server)
        self.closed = True
        with self.lock_close: pass # Wait for run function to end

    def label(self, interface):
        return tuple(interface[1])

    def create_connection(self, interface):
        return TCPConnection(self, interface)

class TCPConnection(stream.Connection):
    def __init__(self, jack, interface, connection=None):
        stream.Connection.__init__(self, jack)

        # Who you're connected to
        self.interface = interface
        self.ifacetype = interface[0]

        # Your connection socket
        if connection:
            self.connection = connection
        else:
            # Construct socket object
            sockaddr = tuple(interface[1])
            if self.ifacetype == 'tcp':
                addrinfo = socket.getaddrinfo(sockaddr[0], sockaddr[1], socket.AF_INET6, socket.SOCK_STREAM)
                (family, socktype, proto, canonname, advsockaddr) = addrinfo[0]
                self.connection = socket.socket(family, socktype, proto)
                self.connection.connect(advsockaddr)
            else:
                self.connection = socket.create_connection(sockaddr)
        self.connection.settimeout(1)
        self.start()

    def run(self):
        while self._running:
            try:
                newdata = self._recv()
            except socket.timeout:
                pass
            except socket.error:
                break
            else:
                self.inject(newdata)
        kill_socket(self.connection)

    @RawDataDecorator(strict=True)
    def _send(self, frame):
        sent = self.connection.send(frame.export())
        logger.info("%d / %d %r -> %r", 
            sent, 
            len(frame), 
            self.connection.getsockname(), 
            self.connection.getpeername()
        )

    @RawDataDecorator(args=False, ret=True, strict=True)
    def _recv(self):
        return self.connection.recv(4096)

def kill_socket(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except socket.error:
        pass # socket already broken
    sock.close()
