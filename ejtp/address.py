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
from json import loads

def str_address(address):
	'''
		Converts address to string, only if it isn't already
		>>> str_address([0,9])
		'[0,9]'
		>>> str_address("[0,9]")
		'[0,9]'
	'''
	if type(address) in (str, unicode):
		return address
	else:
		return strict(address)

def py_address(address):
	'''
		Converts address to non-string, only if it isn't already
		>>> py_address([0,9])
		[0, 9]
		>>> py_address("[0,9]")
		[0, 9]
	'''
	if type(address) in (str, unicode):
		return loads(address)
	else:
		return address
