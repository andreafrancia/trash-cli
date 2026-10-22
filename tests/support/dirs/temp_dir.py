import os
import tempfile

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real.real_fs import RealFs


@pytest.fixture
def temp_dir_fixture():
    temp_dir = make_temp_dir()
    yield temp_dir
    temp_dir.clean_up()

def make_temp_dir():  # type: (...) -> MyPath
    temp_from_os = tempfile.mkdtemp(suffix="_trash_cli_test")
    realpath_just_to_be_sure = os.path.realpath(temp_from_os)
    return MyPath(realpath_just_to_be_sure)

