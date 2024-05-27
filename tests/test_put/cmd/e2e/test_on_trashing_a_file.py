import pytest

from tests.support.dirs.temp_dir import temp_dir
from tests.support.fs_fixture import FsFixture
from tests.test_put.cmd.e2e.run_trash_put import run_trash_put2
from trashcli.put.fs.real_fs import RealFs

temp_dir = temp_dir


@pytest.mark.slow
class TestOnTrashingAFile:
    def setup_method(self):
        self.fx = FsFixture(RealFs())

    def test_in_verbose_mode_should_tell_where_a_file_is_trashed(self,
                                                                 temp_dir):
        env = {'XDG_DATA_HOME': temp_dir / 'XDG_DATA_HOME',
               'HOME': temp_dir / 'home'}
        self.fx.make_empty_file(temp_dir / "foo")

        result = run_trash_put2(temp_dir, ["-v", temp_dir / "foo"], env)

        assert [result.both().cleaned(), result.exit_code] == [
            "trash-put: '/foo' trashed in /XDG_DATA_HOME/Trash\n",
            0
        ]
