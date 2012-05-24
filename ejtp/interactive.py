#!/usr/bin/env python
import datetime
import json

from router import Router
from client import SimpleClient

class Interactive(object):
	def __init__(self, router=None):
		self.router = router or Router()
		self.client = None
		self.messages   = []
		self.encryptors = {}

	def view_messages(self, read=None):
		'''
		>>> inter = Interactive()
		>>> inter.view_messages()
		    No messages.
		>>> inter.receive({'hello':'world'}, ["udp4", ["127.0.0.1", 666], "El Diablo"])
		>>> inter.view_messages() # doctest: +ELLIPSIS
		    All messages:
		--------------------------------------------------------------------------------
		["udp4", ["127.0.0.1", 666], "El Diablo"](at ...):
		{
		    "hello": "world"
		}
		'''
		messages =  (read == None  and self.messages) \
			 or (read == True  and self.read) \
			 or (read == False and self.unread) \
			 or []
		if not len(messages):
			print "    No messages."
			return
		print "    "+self.read_type(read).capitalize()+" messages:"
		for message in messages:
			print "-"*80
			print message

	def receive(self, *args, **kwargs):
		self.messages.append(ReceiveEvent(*args, **kwargs))

	def read_type(self, rt):
		'''
		Convert a True/False/None into the appropriate read filter name.
		>>> inter = Interactive()
		>>> inter.read_type(True)
		'read'
		>>> inter.read_type(False)
		'unread'
		>>> inter.read_type(None)
		'all'
		>>> inter.read_type(3) #doctest +IGNORE_EXCEPTION_DETAIL
		Traceback (most recent call last):
		TypeError: Expected bool or none, got 3
		'''
		if rt==True:
			return "read"
		elif rt==False:
			return "unread"
		elif rt==None:
			return "all"
		else:
			raise TypeError("Expected bool or none, got %r" % rt)

	def set_client(self, interface):
		client = SimpleClient(self.router, interface, lambda x: x)

	def scan_client(self):
		interface = self.scan(
'||| What interface do you want to use? \n\
||| Example: ["udp4", ["192.168.1.5", 5802], "stevey"]\n',
			"Client scan failed",
			json.loads
		)
		#try:
		return self.set_client(interface)
		#except:
		#	print "Failed to create client"

	def scan(self, prompt, failmsg, validator):
		while True:
			try:
				response = raw_input(prompt)
				return validator(response)
			except KeyboardInterrupt:
				quit(1)
			except:
				print failmsg

	def repl(self):
		self.scan_client()
		def validate_command(command):
			command = command.lower()
			if command in (
				'messages',
				'set client',
				'quit',
			):
				return command
			else:
				raise ValueError(command)
		while True:
			command = self.scan(
				'||| Enter a command [messages | set client | quit]\n',
				"That's not a command.",
				validate_command
			)
			if command == "messages":
				self.view_messages()
			elif command == "set client":
				self.scan_client()
			elif command == "quit":
				quit()

	@property
	def read(self):
		return (m for m in self.messages if m.read)

	@property
	def unread(self):
		return (m for m in self.messages if not m.read)


class ReceiveEvent(object):
	'''
	Represents a frame that has arrived.
	'''
	def __init__(self, contents, sender=[], when=None):
		self.contents = contents
		self.sender   = sender
		self.time     = when or datetime.datetime.now()
		self.read     = False

	def reply(self, contents, client):
		pass

	def __str__(self):
		return json.dumps(self.sender)+("(at %r):\n" % self.time)+json.dumps(self.contents, indent=4)

if __name__ == "__main__":
	inter = Interactive()
	inter.repl()
