import os
import unittest

base_path = os.path.split(__file__)[0]

loader = unittest.TestLoader()
tests = loader.discover(base_path)
test_runner = unittest.runner.TextTestRunner()
test_runner.run(tests)