'''
	BaseClient

	Base class for router clients.
'''

from ejtp.util.crypto import make

import frame
import jack

class BaseClient(object):
	def __init__(self, router):
		self.router = router
		self.router._loadclient(self)

	def send(self, msg):
		# Send message to router
		self.router.recv(msg)

	def route(self, msg):
		# Recieve message from router
		raise NotImplementedError("Subclasses of BaseClient must define route()")

class SimpleClient(BaseClient):
	def __init__(self, router, interface, getencryptor, make_jack = True):
		'''
			getencryptor should be a function that accepts an argument "iface"
			and returns an encryptor prototype (2-element list, like ["rotate", 5]).
		'''
		self.interface = interface
		BaseClient.__init__(self, router)
		def get_e(iface):
			return make(getencryptor(iface))
		self.getencryptor = get_e
		if make_jack:
			jack.make(router, interface)

	def route(self, msg):
		# Recieve message from router (will be type 'r' or 's', which contains message)
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
		# Return the message inside a Type R or S
		encryptor = self.getencryptor(msg.addr)
		if encryptor == None:
			msg.raw_decode()
		else:
			if msg.type == "s":
				encryptor = encryptor.flip()
			msg.decode(encryptor)
		#print "Unpacking:",repr(msg.content)
		result = message.Message(msg.content)
		if result.addr == None:
			result.addr = msg.addr
		return result

	def write(self, addr, txt):
		# Write and send a message to addr
		self.owrite([addr], txt)

	def owrite(self, hoplist, txt):
		# Write a message and send through a list of addresses
		self.router.log_add(txt)
		sig_s = self.getencryptor(self.interface).flip()
		msg   = message.make('s', self.interface, sig_s, txt)
		self.router.log_add(msg)
		hoplist = [(a, self.getencryptor(a)) for a in hoplist]
		for m in message.onion(msg, hoplist):
			self.send(m)

	def hello(self, target):
		from ejtp.util.hasher import strict
		iface = self.interface
		obj = {
			"type":"hello",
			"interface":iface,
			"key":self.getencryptor(self.interface).public(),
			"sigs":[]
		}
		enc = self.getencryptor(target)
		msg = message.make('j', None, None, strict(obj))
		for m in message.onion(msg, [(target, enc)]):
			self.send(m)

	# Encryption

	def sign(self, iface, obj):
		enc = self.getencryptor(iface)
		return enc.encrypt(self.hash(obj))

	def sig_verify(self, iface, obj, sig):
		hash = self.hash(obj)
		return hash == self.getencryptor(iface).decode(sig)

	def hash(self, obj):
		txt = strict(obj)
		return make(['sha1']).encrypt(txt)
