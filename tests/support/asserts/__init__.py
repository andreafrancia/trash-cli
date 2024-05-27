import unittest

from tests.support.asserts.comparison import Unidiff


def assert_equals_with_unidiff(expected, actual):
    comparison = Unidiff(expected.splitlines(1),
                            actual.splitlines(1))

    assert expected == actual, ("\n"
                                "Expected:%s\n" % repr(expected) +
                                "  Actual:%s\n" % repr(actual) +
                                comparison.unidiff_as_single_string())


def assert_starts_with(actual, expected):
    class Dummy(unittest.TestCase):
        def nop(self):
            pass

    _t = Dummy('nop')
    _t.assertEqual(actual[:len(expected)], expected)
