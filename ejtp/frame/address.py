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

Contains categories for storing sender and receiver addresses.
'''

from ejtp.frame.base import BaseCategory
from ejtp.address import py_address

class AddressCategory(BaseCategory):
    '''
    Base category for frames that use addresses as their header information.

    Subclasses may override any method, but aren't likely to need to.
    '''

    @property
    def address(self):
        return py_address(self.header)


class SenderCategory(AddressCategory):
    '''
    Frames of this category contain sender information.
    '''
    pass

class ReceiverCategory(AddressCategory):
    '''
    Frames of this category contain receiver information.
    '''
    pass
