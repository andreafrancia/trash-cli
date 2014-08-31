from assert_equals_with_unidiff import assert_equals_with_unidiff

class OutputCollector:
    def __init__(self):
        from StringIO import StringIO
        self.stream = StringIO()
        self.getvalue = self.stream.getvalue
    def write(self,data):
        self.stream.write(data)
    def assert_equal_to(self, expected):
        return self.should_be(expected)
    def assert_equal_any_order(self, expected):
        actual_sorted = sorted(self.stream.getvalue().splitlines(1))
        actual = "".join(actual_sorted)

        expected_sorted = sorted(expected.splitlines(1))
        expected = "".join(expected_sorted)

        assert_equals_with_unidiff(expected, actual)
    def should_be(self, expected):
        assert_equals_with_unidiff(expected, self.stream.getvalue())
    def should_match(self, regex):
        text = self.stream.getvalue()
        from nose.tools import assert_regexp_matches
        assert_regexp_matches(text, regex)

