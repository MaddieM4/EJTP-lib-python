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
	'''
	>>> jack.test_jacks(
	...     ['udp4', ['127.0.0.1', 18999], 'charlie'],
	...     ['udp4', ['127.0.0.1', 19999], 'stacy']
	... )
	Router equality (should be false): False
	UDPJack out: 122 / 122 ('127.0.0.1', 18999) -> (u'127.0.0.1', 19999)
	Client ['udp4', ['127.0.0.1', 19999], 'stacy'] recieved from [u'udp4', [u'127.0.0.1', 18999], u'charlie']: '"A => B"'
	UDPJack out: 122 / 122 ('127.0.0.1', 19999) -> (u'127.0.0.1', 18999)
	Client ['udp4', ['127.0.0.1', 18999], 'charlie'] recieved from [u'udp4', [u'127.0.0.1', 19999], u'stacy']: '"B => A"'
	>>> jack.test_jacks(
	...     ['udp', ['::1', 8999], 'charlie'],
	...     ['udp', ['::1', 9999], 'stacy']
	... )
	Router equality (should be false): False
	UDPJack out: 106 / 106 ('::1', 8999, 0, 0) -> (u'::1', 9999, 0, 0)
	Client ['udp', ['::1', 9999], 'stacy'] recieved from [u'udp', [u'::1', 8999], u'charlie']: '"A => B"'
	UDPJack out: 106 / 106 ('::1', 9999, 0, 0) -> (u'::1', 8999, 0, 0)
	Client ['udp', ['::1', 8999], 'charlie'] recieved from [u'udp', [u'::1', 9999], u'stacy']: '"B => A"'
	'''
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
		location = msg.addr[1]
		if self.ifacetype == 'udp':
			addr = (location[0], location[1], 0,0)
		else:
			addr = (location[0], location[1])
		print "UDPJack out:", len(str(msg)), "/", self.sock.sendto(str(msg), addr), \
			self.address, "->", addr

	def run(self):
		with self.lock_init: pass # Make sure init is done, and ready to run
		self.closed = False
		self.lock_ready.release()
		while not self.closed:
			data = self.sock.recv(frame.PACKET_SIZE)
			self.recv(data)

	def close(self):
		self.closed = True
		self.lock_close.release()
