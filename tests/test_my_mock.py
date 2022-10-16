import unittest

from tests.support.my_mock import MyMock


class TestMyMock(unittest.TestCase):
    def test_existing_method(self):
        a = MyMock({'bar': lambda: "bar-value"})
        assert "bar-value" == a.bar()

    def test_not_existing_method(self):
        a = MyMock()
        self.assertRaises(NotImplementedError, lambda: a.non_existing())
