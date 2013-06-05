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

from persei import RawData, RawDataDecorator

from ejtp.crypto import encryptor

class RotateEncryptor(encryptor.Encryptor):
    def __init__(self, offset):
        self.offset = offset

    @RawDataDecorator(ret=True, strict=True)
    def encrypt(self, source):
        return self.rotate(source, self.offset)

    @RawDataDecorator(ret=True, strict=True)
    def decrypt(self, source):
        return self.rotate(source, -self.offset)
    
    @RawDataDecorator(args=False, ret=True, strict=True)
    def rotate(self, source, offset):
        # not checking args here, because offset would be converted to RawData
        result = RawData()
        for i in source:
            result += (int(i)+offset) % 256
        return result

    def proto(self):
        return ['rotate', self.offset]
