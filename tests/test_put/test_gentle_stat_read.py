import grp
import os
import pwd

from tests.run_command import temp_dir  # noqa
from tests.support.files import make_file
from trashcli.put.reporter import gentle_stat_read


class TestGentleStatRead:
    def test_file_non_found(self, temp_dir):
        result = gentle_stat_read(temp_dir / 'not-existent')

        assert (result.replace(temp_dir, '...') ==
                "[Errno 2] No such file or directory: '.../not-existent'")

    def test_file(self, temp_dir):
        make_file(temp_dir / 'pippo.txt')
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
