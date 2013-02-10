import os
from ejtp.util.compat import unittest

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
