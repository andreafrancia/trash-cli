import pytest

from tests.support.my_path import MyPath


@pytest.fixture
def temp_dir():
    temp_dir = MyPath.make_temp_dir()
    yield temp_dir
    temp_dir.clean_up()
