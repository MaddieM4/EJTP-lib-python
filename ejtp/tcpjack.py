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

import jack
import select
import socket
import frame

class TCPJack(jack.Jack):
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
		self.closed = True

	def route(self, msg, retries = 3):
		# Send frame to somewhere
		location = msg.addr[1]
		sock = self.socket(location)
		strmsg = str(msg)
		try:
			print "TCPJack out:", len(strmsg), "/", sock.send(strmsg), \
				self.address, "->", addr
		except IOError:
			print "TCP send failed. Retrying..."
			self.route(msg, retries-1)

	def run(self):
		self.closed = False
		while not self.closed:
			self.server.listen(5)
			ready_read, ready_write, errored = select.select(
				[self.server]+self.sockets.values(),
				[],
				[],
			)
			if self.server in ready_read:
				conn, addr = self.server.accept()
				self.sockets[addr] = conn
				ready_read.remove(self.server)
			for sock in ready_read:
				self.streams[sock.getpeername()] += sock.recv()
			process_streams()

	def close(self):
		self.closed = True

	def socket(self, address):
		sockaddr = tuple(address[1])
		if sockaddr in self.sockets:
			return self.sockets[sockaddr]
		else:
			s = socket.create_connection(sockaddr)
			s.setblocking(0)
			self.sockets[sockaddr] = s
			self.streams[sockaddr] = ""
			return s

	def process_streams(self):
		# Analyze every stream, eating messages where possible
		for stream in self.streams:
			self.process_stream(stream)

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
