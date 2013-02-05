import os
import sys

if sys.version[:3] in ('2.4', '2.5', '2.6', '3.0', '3.1'):
    import unittest2 as unittest
else:
    import unittest

def main():
    base_path = os.path.split(__file__)[0]
    loader = unittest.TestLoader()
    tests = loader.discover(base_path)
    test_runner = unittest.runner.TextTestRunner()
    results = test_runner.run(tests)
    if not results.wasSuccessful():
        quit(1)

if __name__ == '__main__':
    main()
