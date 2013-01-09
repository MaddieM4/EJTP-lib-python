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

from ejtp.util.py2and3 import is_string
from hashlib import new
import json

HASH_FUNCTION = 'sha1' # was md5

def make(string):
	'''
	Create a hash of a string.

	>>> make("Sample string")
	'e9a47e5417686cf0ac5c8ad9ee90ba2c1d08cc14'
	'''
	return new(HASH_FUNCTION, string).hexdigest()

def make6(string):
	return maken(string, 6)

def maken(string, n):
	return make(string)[:n]

def strict(obj):
	''' Convert an object into a strict JSON string '''
	if isinstance(obj, bool) or obj==None or is_string(obj) or isinstance(obj, int):
		return json.dumps(obj)
	if isinstance(obj, list) or isinstance(obj, tuple):
		return "[%s]" % ",".join([strict(x) for x in obj])
	if isinstance(obj, dict):
		strdict = {}
		for key in obj:
			strdict[str(key)] = obj[key]
		keys = strdict.keys()
		keys.sort()
		return "{%s}" % ",".join([strict(key)+":"+strict(strdict[key]) for key in keys])
	else:
		raise TypeError("Not JSONable: "+str(t))

def strictify(jsonstring):
	''' Make a JSON string strict '''
	return strict(json.loads(jsonstring))

def checksum(obj):
	''' Get the checksum of the strict of an object '''
	return make(strict(obj))

def key(string):
	if len(string)>10:
		return string[:10]+make6(string[10:])
	else:
		return string
