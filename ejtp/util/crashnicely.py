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


import traceback
import sys

class Guard(object):
	'''
	Class of exception catching and printing objects.

	>>> with Guard():
	...     print("This code is okay")
	This code is okay
	>>> with Guard(print_traceback=False):
	... 	print("This code is bad"[""]) # doctest: +ELLIPSIS
	Traceback <traceback object at ...> caught by <ejtp.util.crashnicely.Guard object at ...>
	'''
	def __init__(self, print_catch=True, print_traceback=True):
		# Workaround for doctest being dumb, will fix better later
		self.print_catch = print_catch 
		self.print_traceback = print_traceback

	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if not exc_traceback:
			return True
		if self.print_catch:
			print("Traceback %s caught by %s" % (exc_traceback, self))
		if self.print_traceback:
			traceback.print_exception(exc_type, exc_value, exc_traceback)
		return True

