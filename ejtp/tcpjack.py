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

import frame
import jack
import socket
import threading

class TCPJack(jack.Jack):
	'''
	>>> jack.test_jacks(
	...     ['tcp4', ['127.0.0.1', 18999], 'charlie'],
	...     ['tcp4', ['127.0.0.1', 19999], 'stacy']
	... ) #doctest: +ELLIPSIS
	Router equality (should be false): False
	TCPJack out: 88 / 88 ('127.0.0.1', 18999) -> ('127.0.0.1', ...)
	TCPJack out: 88 / 88 ('127.0.0.1', 19999) -> ('127.0.0.1', ...)
	>>> jack.test_jacks(
	...     ['tcp', ['::1', 8999], 'charlie'],
	...     ['tcp', ['::1', 9999], 'stacy']
	... ) #doctest: +ELLIPSIS
	Router equality (should be false): False
	TCPJack out: 72 / 72 ('::1', 8999, 0, 0) -> ('::1', ..., 0, 0)
	TCPJack out: 72 / 72 ('::1', 9999, 0, 0) -> ('::1', ..., 0, 0)
	'''
	def __init__(self, router, host='::', port=3972, ipv=6):
		if ipv==6:
			ifacetype = "tcp"
			self.address = (host, port, 0, 0)
			sockfamily = socket.AF_INET6
		else: 
			ifacetype = "tcp4"
			self.address = (host, port)
			sockfamily = socket.AF_INET

		jack.Jack.__init__(self, router, (ifacetype, (host, port)))
		self.server = socket.socket(sockfamily, socket.SOCK_STREAM)
		self.server.bind(self.address)
		self.sockets = {}
		self.streams = {}
		self.threads = {}
		self.closed = True
		self.initlock.release()

	def route(self, msg, retries = 3):
		# Send frame to somewhere
		sock = self.socket(msg.addr)
		addr = sock.getsockname()
		strmsg = str(msg)
		try:
			print "TCPJack out:", len(strmsg), "/", sock.send(strmsg), \
				self.address, "->", addr
		except IOError:
			if retries > 0:
				print "TCP send failed. Retrying..."
				self.route(msg, retries-1)
			else:
				print "No retries left."

	def run(self):
		self.initlock.acquire()
		self.initlock.release()
		self.closed = False
		self.server.listen(5)
		while not self.closed:
			conn, addr = self.server.accept()
			conn, addr = self.server.accept()
			self.socket([0, addr[:2]], conn)

	def close(self):
		self.closed = True

	def socket(self, address, conn=None):
		sockaddr = tuple(address[1])
		if sockaddr in self.sockets:
			return self.sockets[sockaddr]
		else:
			if not conn:
				if self.ifacetype == 'tcp':
					addrinfo = socket.getaddrinfo(sockaddr[0], sockaddr[1], socket.AF_INET6, socket.SOCK_STREAM)
					(family, socktype, proto, canonname, advsockaddr) = addrinfo[0]
					conn = socket.socket(family, socktype, proto)
					conn.connect(advsockaddr)
				else:
					conn = socket.create_connection(sockaddr)
			conn.settimeout(1)
			self.sockets[sockaddr] = conn
			self.streams[sockaddr] = ''
			self.threads[sockaddr] = self.sockthread(sockaddr)
			return conn

	def sockthread(self, address):
		def thread_contents():
			while not self.closed:
				try:
					self.streams[address] += self.sockets[address].recv(4096)
					self.process_stream(address)
				except socket.timeout:
					pass
		mythread = threading.Thread(target=thread_contents)
		mythread.start()
		return mythread

	def process_stream(self, streamname):
		data = self.streams[streamname]
		if "." not in data:
			return
		size, content = data.split('.',1)
		size = int(size, 16) # Read size as hex
		if len(content) < size:
			return
		self.recv(content[:size])
		self.streams[streamname] = content[size:]
		self.process_stream(streamname)
