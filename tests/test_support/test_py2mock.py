import os

from tests.support.py2mock import Mock, patch
class TestPy2mock:
    def test_patching(self):
        "This test should work in Python before and after 3.3"
        with patch('os.listdir') as mock_open:
            mock_open.return_value = ["a", "b", "c", "d"]
            result = os.listdir()
        assert result == ["a", "b", "c", "d"]