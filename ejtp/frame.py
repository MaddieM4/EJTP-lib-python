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
	Frame

	Class for EJTP frames.
'''

from ejtp.util import hasher
import json

PACKET_SIZE = 8192

class Frame(object):
	def __init__(self, data):
		if type(data) in (str, unicode, Frame):
			data = str(data)
			self._load(data)

	def _load(self, data):
		self.type = data[0]
		sep = data.index('\x00')
		self.straddr = data[1:sep]
		self.ciphercontent = data[sep+1:]
		if self.type =="j":
			self.content = self.ciphercontent
		if self.straddr:
			self.addr = json.loads(self.straddr)
			if (type(self.addr) != list or len(self.addr)<3):
				raise ValueError("Bad address: "+repr(self.addr))
		else:
			self.addr = None

	def __str__(self):
		return self.type+self.straddr+'\x00'+self.ciphercontent

	def decode(self, encryptor):
		if not self.decoded:
			self.content = encryptor.decrypt(self.ciphercontent)
		return self.content

	def raw_decode(self):
		# Unencrypted content
		self.content = self.ciphercontent

	@property
	def decoded(self):
		return hasattr(self, "content")

def onion(msg, hops=[]):
	'''
		Encrypt a frame into multiple hops.

		Historically, this function supported splitting.
		At some future point we will put this functionality
		back in, but probably as a separate function.
	'''
	hops.reverse()
	for (addr, encryptor) in hops:
		msg = str(make('r', addr, encryptor, str(msg)))
	return msg

def make(type, addr, encryptor, content):
	straddr = ""
	if addr != None:
		straddr = hasher.strict(addr)
	ciphercontent = (encryptor and encryptor.encrypt(content)) or content
	msg = Frame(type +straddr+'\x00'+ciphercontent)
	msg.content = content
	return msg
