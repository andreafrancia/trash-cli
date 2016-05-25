from .assert_equals_with_unidiff import assert_equals_with_unidiff

class OutputCollector:
    def __init__(self):
# Try Python 2 import; if ImportError occurs, use Python 3 import
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        self.stream = StringIO()
        self.getvalue = self.stream.getvalue
    def write(self,data):
        self.stream.write(data)
    def assert_equal_to(self, expected):
        return self.should_be(expected)
    def should_be(self, expected):
        assert_equals_with_unidiff(expected, self.stream.getvalue())
    def should_match(self, regex):
        text = self.stream.getvalue()
        from nose.tools import assert_regexp_matches
        assert_regexp_matches(text, regex)

