import pytest
from tests.support.dirs.temp_dir import temp_dir
from tests.support.files import make_unreadable_file, read_file

@pytest.mark.slow
class TestMakeUnreadableFile:

    def test(self, temp_dir):
        un_readable_path = temp_dir / "unreadable"
        make_unreadable_file(un_readable_path)
        with pytest.raises((OSError, IOError)):
            read_file(un_readable_path)
