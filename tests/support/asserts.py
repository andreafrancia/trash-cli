from textwrap import dedent


def assert_line_in_text(line, text):
    assert line in text.splitlines(), dedent('''\
            Line not found in text
            Line:

            %s

            Text:

            ---
            %s---''') % (repr(line), text)


def assert_equals_with_unidiff(expected, actual):
    def unidiff(expected, actual):
        import difflib
        expected = expected.splitlines(1)
        actual = actual.splitlines(1)

        diff = difflib.unified_diff(expected, actual,
                                    fromfile='Expected', tofile='Actual',
                                    lineterm='\n', n=10)

        return ''.join(diff)

    assert expected == actual, ("\n"
                                "Expected:%s\n" % repr(expected) +
                                "  Actual:%s\n" % repr(actual) +
                                unidiff(expected, actual))
