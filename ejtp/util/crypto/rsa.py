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


import thread
import encryptor

from   Crypto.PublicKey import RSA as rsalib
from   Crypto.Cipher import PKCS1_OAEP
import Crypto.Util.number
from   Crypto.Util.number import ceil_div

class RSA(encryptor.Encryptor):
	def __init__(self, keystr):
		self.keystr = keystr
		self._key = None
		self.genlock = thread.allocate()
		if keystr == None:
			self.genlock.acquire()
			self.generate()
		else:
			self._key = rsalib.importKey(keystr)
			self._cipher = PKCS1_OAEP.new(self._key)

	def encrypt(self, value):
		# Process in blocks
		value  = str(value)
		length = len(value)
		split  = self.input_blocksize
		if length > split:
			return self.encrypt(value[:split]) + self.encrypt(value[split:])
		else:
			return self.cipher.encrypt(value)

	def decrypt(self, value):
		value  = str(value)
		length = len(value)
		split  = self.output_blocksize
		if length > split:
			return self.decrypt(value[:split]) + self.decrypt(value[split:])
		elif length == split:
			return self.cipher.decrypt(value)
		else:
			raise ValueError("Wrong size for ciphertext, expected %d and got %d" % (split, length))

	@property
	def key(self):
		with self.genlock:
			return self._key

	@property
	def cipher(self):
		with self.genlock:
			return self._cipher

	@property
	def keysize(self):
		modBits = Crypto.Util.number.size(self.cipher._key.n)
		return ceil_div(modBits,8)

	@property
	def hashsize(self):
		return self.cipher._hashObj.digest_size

	@property
	def input_blocksize(self):
		# Size to split strings into while encrypting.
		k = self.keysize
		hLen = self.hashsize
		return k - (2*hLen) - 2

	@property
	def output_blocksize(self):
		# Size to split strings into while decrypting.
		return self.keysize

	def generate(self, bits=1024):
		thread.start_new_thread(self._generate, (bits,))

	def _generate(self, bits):
		try:
			self._key = rsalib.generate(bits)
			self._cipher = PKCS1_OAEP.new(self._key)
		finally:
			self.genlock.release()

	def proto(self):
		return ['rsa', self.key.exportKey()]

	def public(self):
		key = self.key.publickey()
		return ['rsa', key.exportKey()]
