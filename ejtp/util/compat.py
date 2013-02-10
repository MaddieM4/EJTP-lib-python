import sys

if (2, 7) <= sys.version_info[:2] < (3, 0) or sys.version_info >= (3, 2):
    import unittest
else:
    import unittest2 as unittest

# Same as sys.version_info.major, but supports pre-2.7
is_py3k = sys.version_info[0] == 3
