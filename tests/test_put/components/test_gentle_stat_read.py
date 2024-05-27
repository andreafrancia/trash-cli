import grp
import os
import pwd

from tests.support.dirs.temp_dir import temp_dir
from tests.support.fs_fixture import FsFixture
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.reporting.stats_reader import gentle_stat_read

temp_dir = temp_dir


class TestGentleStatRead:
    def setup_method(self):
        self.fs = RealFs()
        self.fx = FsFixture(self.fs)

    def test_file_non_found(self, temp_dir):
        result = gentle_stat_read(temp_dir / 'not-existent')

        assert (result.replace(temp_dir, '...') ==
                "[Errno 2] No such file or directory: '.../not-existent'")

    def test_file(self, temp_dir):
        self.fx.make_empty_file(temp_dir / 'pippo.txt')
        os.chmod(temp_dir / 'pippo.txt', 0o531)

        result = gentle_stat_read(temp_dir / 'pippo.txt')

        assert result == '531 %s %s' % (
            self.current_user(), self.current_group()
        )

    @staticmethod
    def current_user():
        return pwd.getpwuid(os.getuid()).pw_name

    @staticmethod
    def current_group():
        return grp.getgrgid(os.getgid()).gr_name
