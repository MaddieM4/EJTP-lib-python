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
	Jack

	Base class for jacks. Each jack handles routing inbound and outbound
	for an address type, like UDP or Email.
'''
import threading

class Jack(object):
	def __init__(self, router, interface):
		self.initlock = threading.Lock()
		self.initlock.acquire()
		self.router = router
		self.interface = interface
		self.router._loadjack(self)

	def run(self):
		# Receive loop
		raise NotImplementedError("Subclasses of Jack must define run")

	def close(self):
		# Stop the loop
		raise NotImplementedError("Subclasses of Jack must define close")

	def route(self, msg):
		# Send a message.Message from the router (assumes full flush)
		raise NotImplementedError("Subclasses of Jack must define route")

	def recv(self, data):
		# Send a string to the router (must be complete message)
		self.router.recv(data)

	def run_threaded(self):
		if hasattr(self, "closed") and self.closed==False:
			# Already running
			return None
		import thread
		self.thread = thread.start_new_thread(self.run, ())

	@property
	def ifacetype(self):
		return self.interface[0]

def make(router, iface):
	t = iface[0]
	# UDP Jack
	if t == "udp":
		import udpjack
		host, port = iface[1]
		return udpjack.UDPJack(router, host=host, port=port)
	elif t == "udp4":
		import udpjack
		host, port = iface[1]
		return udpjack.UDPJack(router, host=host, port=port, ipv=4)

	# TCP Jack
	elif t == "tcp":
		import tcpjack
		host, port = iface[1]
		return tcpjack.TCPJack(router, host=host, port=port)
	elif t == "tcp4":
		import tcpjack
		host, port = iface[1]
		return tcpjack.TCPJack(router, host=host, port=port, ipv=4)

def test_jacks(ifaceA, ifaceB):
	# Tests client communication across distinct routers.
	# The printed output can be used for unit testing.
	import router, client
	routerA = router.Router()
	routerB = router.Router()
	clientA = client.Client(routerA, ifaceA)
	clientB = client.Client(routerB, ifaceB)
	print "Router equality (should be false):", clientA.router == clientB.router
	# Share encryptor data
	clientA.encryptor_cache = clientB.encryptor_cache
	clientA.encryptor_set(ifaceA, ['rotate', 43])
	clientA.encryptor_set(ifaceB, ['rotate', 93])
	# Syncronize for output consistency
	transfer_condition = threading.Condition() # Prevent transfers from clobbering each other
	transfer_condition.acquire()
	print_lock = threading.Lock() # Prevent prints within a transfer from colliding
	def rcv_callback(msg, client_obj):
		print_lock.acquire()
		print "Client %r recieved from %r: %r" % (client_obj.interface, msg.addr, msg.content)
		transfer_condition.notify()
		print_lock.release()
	# Do the test
	print_lock.acquire()
	clientA.write_json(ifaceB, "A => B")
	print_lock.release()
	transfer_condition.wait(2)

	print_lock.acquire()
	clientB.write_json(ifaceA, "B => A")
	print_lock.release()
	transfer_condition.wait(2)

	# Clean up
	routerA.stop_all()
	routerB.stop_all()
