'''
This module is an alias so that people can migrate to using "ejtp.crypto"
instead of "ejtp.util.crypto" before the latter is deprecated.

It supports most import use cases, but not all. It shouldn't break any
existing code, of course, because nothing is using the alias yet.

>>> import ejtp.crypto
>>> dir(ejtp.crypto)
['__builtins__', '__doc__', '__file__', '__name__', '__package__', 'aes', 'bin_unicode', 'encryptor', 'make', 'rotate', 'rsa']
>>> from ejtp.crypto import aes

And here's where we hit our limits. The alias is a module, not a package - it
contains the submodules by importing them, so using import mechanisms that will
try to find the submodules via the filesystem... won't work. Note that this is
just a shortcoming of the alias, which will go away with EJTP v0.9.

>>> import ejtp.crypto.rotate
Traceback (most recent call last):
ImportError: No module named rotate

>>> from ejtp.crypto.rotate import RotateEncryptor
Traceback (most recent call last):
ImportError: No module named rotate
'''

from ejtp.util.crypto import encryptor, make, bin_unicode
from ejtp.util.crypto import *
