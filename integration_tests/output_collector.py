class OutputCollector:
    def __init__(self):
        from StringIO import StringIO
        self.stream = StringIO()
        self.getvalue = self.stream.getvalue
    def write(self,data):
        self.stream.write(data)
    def assert_equal_to(self, expected):
        return self.should_be(expected)
    def should_be(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.stream.getvalue())
    def should_match(self, regex):
        text = self.stream.getvalue()
        from nose.tools import assert_regexp_matches
        assert_regexp_matches(text, regex)

