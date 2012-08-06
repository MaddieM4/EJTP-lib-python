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
import streamjack

class TCPJack(streamjack.StreamJack):
    '''
    >>> import core as jack
    >>> jack.test_jacks(
    ...     ['tcp4', ['127.0.0.1', 18999], 'charlie'],
    ...     ['tcp4', ['127.0.0.1', 19999], 'stacy']
    ... ) #doctest: +ELLIPSIS
    Router equality (should be false): False
    TCPJack out: 125 / 125 ('127.0.0.1', ...) -> ('127.0.0.1', 19999)
    Client ['tcp4', ['127.0.0.1', 19999], 'stacy'] recieved from [u'tcp4', [u'127.0.0.1', 18999], u'charlie']: '"A => B"'
    TCPJack out: 125 / 125 ('127.0.0.1', ...) -> ('127.0.0.1', 18999)
    Client ['tcp4', ['127.0.0.1', 18999], 'charlie'] recieved from [u'tcp4', [u'127.0.0.1', 19999], u'stacy']: '"B => A"'
    >>> jack.test_jacks(
    ...     ['tcp', ['::1', 8999], 'charlie'],
    ...     ['tcp', ['::1', 9999], 'stacy']
    ... ) #doctest: +ELLIPSIS
    Router equality (should be false): False
    TCPJack out: 109 / 109 ('::1', ..., 0, 0) -> ('::1', 9999, 0, 0)
    Client ['tcp', ['::1', 9999], 'stacy'] recieved from [u'tcp', [u'::1', 8999], u'charlie']: '"A => B"'
    TCPJack out: 109 / 109 ('::1', ..., 0, 0) -> ('::1', 8999, 0, 0)
    Client ['tcp', ['::1', 8999], 'charlie'] recieved from [u'tcp', [u'::1', 9999], u'stacy']: '"B => A"'
    '''
    def __init__(self, router, host='::', port=3972, ipv=6):
        if ipv==6:
            ifacetype = "tcp"
            self.address = (host, port, 0, 0)
            self.sockfamily = socket.AF_INET6
        else: 
            ifacetype = "tcp4"
            self.address = (host, port)
            self.sockfamily = socket.AF_INET

        streamjack.StreamJack.__init__(self, router, (ifacetype, (host, port)))
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
                    #print "New incoming connection to %r: %r %r" % (self.interface, addr, interface)
                    self.add_connection(interface, 
                        TCPConnection(self, interface, connection=conn)
                    )
                except socket.error, e:
                    pass
            for conn in self.connections.values():
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

class TCPConnection(streamjack.Connection):
    def __init__(self, jack, interface, connection=None):
        streamjack.Connection.__init__(self, jack)

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

    def _send(self, frame):
        print "TCPJack out:", self.connection.send(frame), "/", len(frame), self.connection.getsockname(), "->", self.connection.getpeername()

    def _recv(self):
        return self.connection.recv(4096)

def kill_socket(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except socket.error:
        pass # socket already broken
    sock.close()
