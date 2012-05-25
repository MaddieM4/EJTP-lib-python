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

import jack
import socket
import frame

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

	def route(self, msg):
		# Send frame to somewhere
		location = msg.addr[1]
		if self.ifacetype == 'udp':
			addr = (location[0], location[1], 0,0)
		else:
			addr = (location[0], location[1])
		print addr
		print "UDPJack out:", len(str(msg)), "/", self.sock.sendto(str(msg), addr), \
			self.address, "->", addr
		#print repr(str(msg))

	def run(self):
		self.closed = False
		while not self.closed:
			data = self.sock.recv(frame.PACKET_SIZE)
			self.recv(data)

	def close(self):
		self.closed = True
