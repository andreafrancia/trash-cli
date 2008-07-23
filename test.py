import sys
import unittest
sys.path.append('test')
sys.path.append('src')
import libtrash_test

suite = unittest.TestLoader().loadTestsFromModule(libtrash_test)
unittest.TextTestRunner(verbosity=3).run(suite)

