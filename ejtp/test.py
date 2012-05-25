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


#!/usr/bin/env python

import doctest
import ejtp

def test_recursive(mod, debug=False):
	(failure_count, test_count) = doctest.testmod(mod)
	if "__all__" in dir(mod):
		for child in mod.__all__:
			fullchildname = mod.__name__+"."+child
			if debug:
				print "Testing", fullchildname
			childmod = __import__(fullchildname, fromlist=[""])
			cf, ct = test_recursive(childmod, debug)
			failure_count += cf
			test_count    += ct
	return (failure_count, test_count)

def test_ejtp(debug = False):
	failures, tests = test_recursive(ejtp, debug)
	print "%d failures, %d tests." % (failures, tests)

if __name__ == "__main__":
	import sys
	debug = "-l" in sys.argv
	test_ejtp(debug)
