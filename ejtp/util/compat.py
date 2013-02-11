import sys

if (2, 7) <= sys.version_info[:2] < (3, 0) or sys.version_info >= (3, 2):
    import unittest
else:
    import unittest2 as unittest

try:
    import json
except ImportError:
    import simplejson as json

# Same as sys.version_info.major, but supports pre-2.7
is_py3k = sys.version_info[0] == 3

def get_exception():
    return sys.exc_info()[1]

# Python 2.5 does not have format builtin
try:
    format = format
except NameError:
    def format(value, spec): # TODO: is it right?
        f ='%' + spec
        return f % value

# Python 2.5 does not have bytes builtin
try:
    bytes = bytes
except NameError:
    bytes = str

# Python 3+ moved cStringIO to io module
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
