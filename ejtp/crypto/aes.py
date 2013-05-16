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

from persei import RawData, RawDataDecorator, StringDecorator

from ejtp.crypto import encryptor

from Crypto.Hash import SHA
from Crypto.Cipher import AES

class AESEncryptor(encryptor.Encryptor):
    @StringDecorator(strict=True)
    def __init__(self, password):
        self.password = password
        hash = SHA.new(password.toRawData().export()).digest()
        self.cipher = AES.new(hash[:16]) # Must be multiple of 16, cuts 20 char digest to 16 char

    @RawDataDecorator(ret=True, strict=True)
    def encrypt(self, value):
        # Uses custom format to encrypt arbitrary length strings with padding
        code = RawData(len(value)) + "\x00" + value
        code += (16 - len(code) % 16) * "\x00"
        return self.cipher.encrypt(code.export())

    @RawDataDecorator(ret=True, strict=True)
    def decrypt(self, value):
        code = RawData(self.cipher.decrypt(value.export()))
        split = code.index('\x00')
        length = int(code[:split])
        code = code[split+1:]
        return code[:length]

    def proto(self):
        return ['aes', self.password]
