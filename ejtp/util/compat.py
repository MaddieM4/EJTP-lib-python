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