import os

import pytest

from tests.support.dirs.my_path import MyPath
from trashcli.fslib.real.real_fs import RealFs


@pytest.fixture
def temp_dir_fixture():
    fs = RealFs()
    temp_dir = make_temp_dir(fs)
    yield temp_dir
    temp_dir.clean_up()

def make_temp_dir(fs):  # type: (RealFs) -> MyPath
    temp_from_os = fs.mkdtemp(suffix="_trash_cli_test")
    realpath_just_to_be_sure = os.path.realpath(temp_from_os)
    return MyPath(realpath_just_to_be_sure)

