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


from ejtp.address import Address
from ejtp.util.compat import unittest
from ejtp.util.hasher import strict


class TestAddress(unittest.TestCase):
    def test_init(self):
        self.assertEqual(Address('myproto', ('foo', 'bar'), 'Peter'), ('myproto', ('foo', 'bar'), 'Peter'))
        self.assertEqual(Address('myproto', ('foo', 'bar')), ('myproto', ('foo', 'bar'), None))
        self.assertEqual(Address(addrtype='myproto', addrdetails=('foo', 'bar'), callsign='Peter'), ('myproto', ('foo', 'bar'), 'Peter'))
        self.assertEqual(Address(addrtype='myproto', addrdetails=('foo', 'bar')), ('myproto', ('foo', 'bar'), None))

    def test_create(self):
        self.assertEqual(Address.create('["myproto", ["foo", "bar"], "Peter"]'), Address('myproto', ['foo', 'bar'], 'Peter'))
        self.assertEqual(Address.create('["myproto", ["foo", "bar"]]'), Address('myproto', ['foo', 'bar'], None))
        self.assertRaises(TypeError, Address.create, object())
        #self.assertRaises(ValueError, Address.create, '["foo"]')
        self.assertRaises(ValueError, Address.create, '["foo", "bar", "baz", "foobarbaz"]')

    def test_export(self):
        self.assertEqual(Address('myproto', ('foo', 'bar'), 'Peter').export(), strict(['myproto', ['foo', 'bar'], 'Peter']))

