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

from persei import String

from ejtp.util.compat import unittest
from ejtp.address import str_address, py_address

class TestPyAddress(unittest.TestCase):

    def _assert(self, expected, value):
        self.assertEqual(expected, py_address(value))

    def test_with_string(self):
        self._assert([0, 9], '[0,9]')

    def test_with_list(self):
        self._assert([0, 9], [0, 9])


class TestStrAddress(unittest.TestCase):

    def _assert(self, expected, value):
        self.assertEqual(expected, str_address(value))

    def test_with_string(self):
        self._assert(String('[0,9]'), '[0,9]')

    def test_with_list(self):
        self._assert(String('[0,9]'), [0, 9])
