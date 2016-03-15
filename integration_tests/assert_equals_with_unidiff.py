# Copyright (C) 2009-2011 Andrea Francia Trivolzio(PV) Italy

def assert_equals_with_unidiff(expected, actual):
    def unidiff(expected, actual):
        import difflib
        expected=expected.splitlines(1)
        actual=actual.splitlines(1)

        diff=difflib.unified_diff(expected, actual,
                                 fromfile='Expected', tofile='Actual',
                                 lineterm='\n', n=10)

        return ''.join(diff)
    from nose.tools import assert_equal
    assert_equal(expected, actual,
                  "\n"
                  "Expected:%s\n" % repr(expected) +
                  "  Actual:%s\n" % repr(actual) +
                  unidiff(expected, actual))
