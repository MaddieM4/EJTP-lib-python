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

from persei import RawData

from ejtp.util.compat import unittest
from ejtp import frame

import zlib
import bz2

class TestCompressor(unittest.TestCase):
    def test_init(self):
        self.assertEqual(frame.compressed.Compressor('foobar')._data, RawData('foobar'))
    
    def test_compress(self):
        self.assertRaises(NotImplementedError, frame.compressed.Compressor('foobar').compress)
    
    def test_decompress(self):
        self.assertRaises(NotImplementedError, frame.compressed.Compressor('foobar').decompress)


class TestZlibCompressor(unittest.TestCase):
    def test_compress(self):
        self.assertEqual(frame.compressed.ZlibCompressor('foobar').compress(), RawData(zlib.compress(RawData('foobar').export())))
    
    def test_decompress(self):
        compressed = zlib.compress(RawData('foobar').export())
        self.assertEqual(frame.compressed.ZlibCompressor(compressed).decompress(), RawData('foobar'))
        self.assertRaises(frame.compressed.CompressionError, frame.compressed.ZlibCompressor('foobar').decompress)


class TestBz2Compressor(unittest.TestCase):
    def test_compress(self):
        self.assertEqual(frame.compressed.Bz2Compressor('foobar').compress(), RawData(bz2.compress(RawData('foobar').export())))
    
    def test_decompress(self):
        compressed = bz2.compress(RawData('foobar').export())
        self.assertEqual(frame.compressed.Bz2Compressor(compressed).decompress(), RawData('foobar'))
        self.assertRaises(frame.compressed.CompressionError, frame.compressed.Bz2Compressor('foobar').decompress)


class TestCompressedFrame(unittest.TestCase):
    def test_registration(self):
        self.assertEqual(frame.createFrame('c\x00'), frame.compressed.CompressedFrame('c\x00'))
    
    def test_construct(self):
        for comp_t, comp in frame.compressed._compression_types.items():
            compressed = comp('foobar').compress()
            self.assertEqual(frame.compressed.construct('foobar', comp_t),
                frame.compressed.CompressedFrame(RawData('c') + comp_t + '\x00' + compressed))

        for comp_alias, comp_t in frame.compressed._compression_alias.items():
            self.assertEqual(frame.compressed.construct('foobar', comp_alias),
                frame.compressed.construct('foobar', comp_t))
        
        self.assertRaises(ValueError, frame.compressed.construct, 'foobar', 'unkknown')
    
    def test_decode(self):
        self.assertEqual(frame.compressed.construct('foobar', 'z').decode(), RawData('foobar'))
        self.assertRaises(ValueError, frame.compressed.CompressedFrame('cunknown\x00foobar').decode)
