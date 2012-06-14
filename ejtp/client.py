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

from ejtp.util.crypto import make
from ejtp.util.hasher import strict

from address import *
import frame
import jack

class Client(object):
	def __init__(self, router, interface, encryptor_cache = None, make_jack = True):
		'''
			encryptor_get should be a function that accepts an argument "iface"
			and returns an encryptor prototype (2-element list, like ["rotate", 5]).
		'''
		self.interface = interface
		self.router = router
		self.router._loadclient(self)
		self.encryptor_cache = encryptor_cache or dict()
		if make_jack:
			jack.make(router, interface)

	def send(self, msg):
		# Send frame to router
		self.router.recv(msg)

	def route(self, msg):
		# Recieve frame from router (will be type 'r' or 's', which contains message)
		self.router.log_add(msg)
		if msg.type == 'r':
			if msg.addr != self.interface:
				self.send(msg)
			else:
				self.route(self.unpack(msg))
		elif msg.type == 's':
			self.route(self.unpack(msg))
		elif msg.type == 'a':
			print "Ack:", msg.content
		elif msg.type == 'j':
			self.rcv_callback(msg, self)
		elif msg.type == 'p':
			print "Part:", msg.content

	def rcv_callback(self, msg, client_obj):
		print "Recieved from %s: %s" % (repr(msg.addr),repr(msg.content))

	def unpack(self, msg):
		# Return the frame inside a Type R or S
		encryptor = self.encryptor_get(msg.addr)
		if encryptor == None:
			msg.raw_decode()
		else:
			if msg.type == "s":
				encryptor = encryptor.flip()
			msg.decode(encryptor)
		#print "Unpacking:",repr(msg.content)
		result = frame.Frame(msg.content)
		if result.addr == None:
			result.addr = msg.addr
		return result

	def write(self, addr, txt, wrap_sender=True):
		# Write and send a frame to addr
		self.owrite([addr], txt, wrap_sender)

	def owrite(self, hoplist, msg, wrap_sender=True):
		# Write a frame and send through a list of addresses
		self.router.log_add(">>> "+msg)
		if wrap_sender:
			sig_s = self.encryptor_get(self.interface).flip()
			msg   = frame.make('s', self.interface, sig_s, msg)
			self.router.log_add(msg)
		hoplist = [(a, self.encryptor_get(a)) for a in hoplist]
		for m in frame.onion(msg, hoplist):
			self.send(m)

	def write_json(self, addr, data, wrap_sender=True):
		msg = frame.make('j', None, None, strict(data))
		self.write(addr, str(msg), wrap_sender)

	def hello(self, target):
		iface = self.interface
		obj = {
			"type":"hello",
			"interface":iface,
			"key":self.encryptor_get(self.interface).public(),
			"sigs":[]
		}
		self.write_json(target, obj, False)

	# Encryption

	def sign(self, iface, obj):
		enc = self.encryptor_get(iface)
		return enc.encrypt(self.hash(obj))

	def sig_verify(self, iface, obj, sig):
		hash = self.hash(obj)
		return hash == self.encryptor_get(iface).decode(sig)

	def hash(self, obj):
		txt = strict(obj)
		return make(['sha1']).encrypt(txt)

	def encryptor_get(self, address):
		address = str_address(address)
		return make(self.encryptor_cache[address])
