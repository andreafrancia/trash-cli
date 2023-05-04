def assert_that(value, matcher):
    assert matcher.matches(value), matcher.describe_mismatch(value)
