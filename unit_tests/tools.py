try:
    from nose.tools import assert_items_equal
except ImportError:
    from nose.tools import assert_count_equal as assert_items_equal
