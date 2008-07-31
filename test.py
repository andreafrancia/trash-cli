import sys
import unittest
sys.path.insert(0,'src')
import libtrash
import libtrash.tests

suite = unittest.TestLoader().loadTestsFromModule(libtrash.tests)
unittest.TextTestRunner(verbosity=3).run(suite)
