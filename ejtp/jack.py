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

class Jack(object):
	def __init__(self, router, interface):
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
		# Send a message.Message from the router
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
	if t == "udp":
		import udpjack
		host, port = iface[1]
		return udpjack.UDPJack(router, host=host, port=port)
	elif t == "udp4":
		import udpjack
		host, port = iface[1]
		return udpjack.UDPJack(router, host=host, port=port, ipv=4)
