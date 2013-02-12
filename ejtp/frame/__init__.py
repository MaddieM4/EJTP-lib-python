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

__all__ = ['createFrame', 'RegisterFrame']

# importing all builtin Frames to make them register themselves
_builtin_frames = ('ejtp.frame.encrypted', 'ejtp.frame.signed', 'ejtp.frame.json')
try:
    from importlib import import_module
except ImportError:
    import_module = __import__

for f in _builtin_frames:
    import_module(f)


from ejtp.util.py2and3 import RawDataDecorator
from ejtp.frame import registration

@RawDataDecorator(strict=True)
def createFrame(char):
    '''
    Returns subclass of BaseFrame represented by char or throws
    NotImplementedError if char is not registered.
    '''
    
    cls = registration._frametypes.get(char)
    if cls is None:
        raise NotImplementedError('char is not registered')
    return cls


