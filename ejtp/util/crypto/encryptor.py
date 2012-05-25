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


from ejtp.util.hasher import strict

class Encryptor(object):
	def encrypt(self, s):
		raise NotImplementedError("Encryptor must define 'encrypt'")

	def decrypt(self, s):
		raise NotImplementedError("Encryptor must define 'decrypt'")

	def public(self):
		# Returns a prototype for the public version of the key.
		# Assumes shared key = your key, overwrite for key types
		# where your public key and private key are different.
		return self.proto()

	def flip(self):
		return Flip(self)

	def __str__(self):
		return strict(self.proto())

class Flip(Encryptor):
	def __init__(self, parent):
		self.encrypt = parent.decrypt
		self.decrypt = parent.encrypt

def make(data):
	if type(data) in (str, unicode):
		import json
		data = json.loads(data)
	t = data[0]
	args = data[1:]
	if t=="rotate":
		import rotate
		return rotate.RotateEncryptor(*args)
	elif t=="aes":
		import aes
		return aes.AESEncryptor(*args)
	elif t=="rsa":
		import rsa
		return rsa.RSA(*args)
	else:
		raise TypeError("Unsupported encryption type: "+str(data))
