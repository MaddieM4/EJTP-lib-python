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

__all__ = [
    'createFrame',
    'RegisterFrame',
    'address',
    'base',
    'encrypted',
    'signed',
    'json',
    'compressed',
    'registration',
]

__doctestall__ = [
    'address',
    'base',
    'encrypted',
    'signed',
    'json',
    'registration',
]

from ejtp.frame.registration import createFrame, RegisterFrame

# importing all builtin Frames to make them register themselves
_builtin_frames = ('ejtp.frame.encrypted', 'ejtp.frame.signed', 'ejtp.frame.json', 'ejtp.frame.compressed')

def init():
    try:
        from importlib import import_module
    except ImportError:
        import_module = __import__

    for f in _builtin_frames:
        import_module(f)

init()
