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

__all__ = ['CompressedFrame', 'construct']

from persei import RawData, String, RawDataDecorator

from ejtp.frame.base import BaseFrame
from ejtp.frame.registration import RegisterFrame
from ejtp.util.hasher import strict

import bz2
import zlib

class CompressionError(Exception):
    '''
    Gets thrown if a errors occurs during (de)compression
    '''
    pass


class Compressor(object):
    '''
    Contains methods to compress and decompress data.
    '''

    @RawDataDecorator(strict=True)
    def __init__(self, data):
        self._data = data
    
    @RawDataDecorator(args=False, ret=True, strict=True)
    def compress(self):
        '''
        Compresses given data.
        '''
        raise NotImplementedError('each subclass of Compressor must implement compress')

    @RawDataDecorator(args=False, ret=True, strict=True)   
    def decompress(self):
        '''
        Decompresses given data.
        '''
        raise NotImplementedError('each subclass of Compressor must implement decompress')


class ZlibCompressor(Compressor):
    @RawDataDecorator(args=False, ret=True, strict=True)
    def compress(self):
        try:
            return zlib.compress(self._data.export())
        except zlib.error:
            raise CompressionError()
    
    @RawDataDecorator(args=False, ret=True, strict=True)
    def decompress(self):
        try:
            return zlib.decompress(self._data.export())
        except zlib.error:
            raise CompressionError()


class Bz2Compressor(Compressor):
    @RawDataDecorator(args=False, ret=True, strict=True)
    def compress(self):
        return bz2.compress(self._data.export())

    @RawDataDecorator(args=False, ret=True, strict=True)
    def decompress(self):
        try:
            return bz2.decompress(self._data.export())
        except IOError:
            raise CompressionError()


_compression_types = {
    RawData('z'): ZlibCompressor,
    RawData('b'): Bz2Compressor
}


@RegisterFrame('c')
class CompressedFrame(BaseFrame):
    
    @RawDataDecorator(args=False, ret=True, strict=True)
    def decode(self, ident_cache = None):
        if self.header not in _compression_types:
            raise ValueError('unknown compression type')
        compressor = _compression_types[self.header]
        return compressor(self.body).decompress()


_compression_alias = {
    String('zlib'): RawData('z'),
    String('gzip'): RawData('z'),
    String('bzip'): RawData('b'),
    String('bzip2'): RawData('b'),
    String('bz2'): RawData('b')
}


def construct(content, compression_type):
    c_type = String(compression_type)
    if c_type in _compression_alias:
        c_type = _compression_alias[c_type]
    elif c_type.toRawData() in _compression_types:
        c_type = c_type.toRawData()
    else:
        raise ValueError('unknown compression_type')
    return CompressedFrame(
        RawData('c') + c_type + RawData(0) + \
        RawData(_compression_types[c_type](content).compress())
    )
