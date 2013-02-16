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

from ejtp.util.compat import unittest

from ejtp.util.py2and3 import RawData, String, RawDataDecorator, StringDecorator

from random import randint
import sys

class TestRawData(unittest.TestCase):
    def test_init(self):
        self.assertEqual(RawData(RawData('abc')), RawData('abc'))
        self.assertEqual(RawData(97), RawData('a'))
        self.assertEqual(RawData([97, 98, 99]), RawData('abc'))
        self.assertRaises(TypeError, lambda: RawData(object()))
        self.assertEqual(RawData(String('abc')), RawData('abc'))
        self.assertRaises(ValueError, lambda: RawData(('a',)))
        self.assertRaises(ValueError, lambda: RawData(300))

    def test_eq(self):
        self.assertEqual(RawData('abc'), RawData((97, 98, 99)))
        self.assertNotEqual(RawData('abc'), 'abc')
    
    def test_add(self):
        self.assertEqual(RawData('ab') + RawData('c'), RawData('abc'))
        self.assertEqual(RawData('ab') + 99, RawData('abc'))
        self.assertRaises(TypeError, lambda: RawData('ab') + object())
    
    def test_len(self):
        for i in range(100):
            l = randint(1,1000)
            self.assertEqual(len(RawData((0,)*l)), l)
    
    def test_getitem(self):
        self.assertEqual(RawData('abc')[1], RawData('b'))
    
    def test_contains(self):
        self.assertTrue(RawData('a') in RawData('abc'))
        self.assertTrue('a' in RawData('abc'))
        self.assertTrue(97 in RawData('abc'))
    
    def test_iter(self):
        self.assertEqual(tuple(iter(RawData('abc'))), (97, 98, 99))
    
    def test_hash(self):
        self.assertEqual(hash(RawData('abc')), hash((97, 98, 99)))
    
    def test_repr(self):
        self.assertEqual(repr(RawData('abc')), 'RawData((0x61,0x62,0x63))')
    
    def test_int(self):
        self.assertEqual(int(RawData('a')), 97)
        self.assertRaises(TypeError, lambda: int(RawData('abc')))
    
    def test_index(self):
        r = RawData('abc')
        self.assertEqual(r.index(RawData('b')), 1)
        self.assertEqual(r.index(99), 2)
        self.assertRaises(TypeError, lambda: r.index(RawData('ab')))
        self.assertRaises(TypeError, lambda: r.index(300))
        self.assertRaises(ValueError, lambda: r.index(RawData('d')))
    
    def test_split(self):
        self.assertEqual(RawData('a:b:c').split(':'), [RawData('a'), RawData('b'), RawData('c')])
        self.assertEqual(RawData('a:b:c').split(':', 1), [RawData('a'), RawData('b:c')])

    def test_tostring(self):
        self.assertEqual(RawData('abc').toString(), String('abc'))
        self.assertRaises(UnicodeDecodeError, lambda: RawData(b'\xc3').toString())

    def test_export(self):
        self.assertEqual(RawData(RawData('abc').export()), RawData('abc'))

class TestString(unittest.TestCase):
    def test_init(self):
        self.assertEqual(String(String('abc')), String('abc'))
        self.assertEqual(String(RawData('abc')), String('abc'))
        self.assertRaises(TypeError, lambda: String(RawData(0xc3)))
        self.assertRaises(TypeError, lambda: String(123))
    
    def test_eq(self):
        self.assertEqual(String('abc'), String('abc'))
        self.assertNotEqual(String('abc'), 'abc')
    
    def test_lt(self):
        self.assertTrue(String('abc') < String('bbc'))
        self.assertFalse(String('abc') < String('abc'))
        self.assertFalse(String('bbc') < String('abc'))
    
    def test_add(self):
        self.assertEqual(String('ab') + String('c'), String('abc'))
        self.assertEqual(String('ab') + 'c', String('abc'))
        self.assertEqual(String('ab') + RawData('c'), String('abc'))
        self.assertRaises(TypeError, lambda: String('abc') + object())
    
    def test_len(self):
        for i in range(100):
            l = randint(1, 1000)
            self.assertEqual(len(String('0'*l)), l)
    
    def test_getitem(self):
        self.assertEqual(String('abc')[1], String('b'))
    
    def test_iter(self):
        self.assertEqual(tuple(iter(String('abc'))), ('a', 'b', 'c'))
  
    def test_hash(self):
        if (sys.version_info.major == 2):      
            self.assertEqual(hash(String('abc')), hash(unicode('abc')))
        elif (sys.version_info.major >= 3):
            self.assertEqual(hash(String('abc')), hash('abc'))
        
    def test_repr(self):
        self.assertEqual(repr(String('abc')), "String('abc')")
    
    def test_index(self):
        s = String('abc')
        self.assertEqual(s.index('bc'), 1)
        self.assertEqual(s.index(String('bc')), 1)
        self.assertRaises(TypeError, lambda: s.index(1))
        self.assertRaises(ValueError, lambda: s.index('d'))
    
    def test_join(self):
        self.assertEqual(String(',').join(('a', 'b', 'c')), String('a,b,c'))
        self.assertRaises(TypeError, lambda: String('').join(123))
    
    def test_torawdata(self):
        self.assertEqual(String('abc').toRawData(), RawData('abc'))
    
    def test_export(self):
        self.assertEqual(String(String('abc').export()), String('abc'))
