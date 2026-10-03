import pytest

from tests.support.merge_dicts import merge_dicts


class TestMergeDicts:
    def test_two_dicts(self):
        assert merge_dicts({'a': 1}, {'b': 2}) == {'a': 1, 'b': 2}

    def test_three_dicts(self):
        assert merge_dicts({'a': 1}, {'b': 2}, {'c': 3}) == {'a': 1,
                                                              'b': 2,
                                                              'c': 3}

    def test_the_last_wins(self):
        assert merge_dicts({'a': 1}, {'a': 2}, {'a': 3}) == {'a': 3}

    def test_the_inputs_are_not_modified(self):
        x, y, z = {'a': 1}, {'b': 2}, {'c': 3}

        merge_dicts(x, y, z)

        assert (x, y, z) == ({'a': 1}, {'b': 2}, {'c': 3})

    def test_returns_a_new_dict(self):
        x = {'a': 1}

        assert merge_dicts(x, {}) is not x

    def test_less_than_two_dicts_is_an_error(self):
        with pytest.raises(TypeError):
            merge_dicts({'a': 1})
