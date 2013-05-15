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

from persei import RawData, StringDecorator

from ejtp.frame.base import BaseFrame
from ejtp.frame.registration import RegisterFrame
from ejtp.util.hasher import strict

@RegisterFrame('j')
class JSONFrame(BaseFrame):
    
    @StringDecorator(args=False, ret=True, strict=True)
    def decode(self, ident_cache = None):
        return self.body

def construct(content):
    return JSONFrame(
        RawData('j\x00') + \
        RawData(strict(content))
    )
