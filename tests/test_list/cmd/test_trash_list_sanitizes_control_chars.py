import os
import unittest

from six import StringIO

from tests.support.dirs.my_path import MyPath
from trashcli.empty.main import FileSystemContentReader
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirRulesReader
from trashcli.file_system_reader import FileSystemReader
from trashcli.fstab.volume_listing import FixedVolumesListing
from trashcli.lib.dir_reader import RealDirReader
from tests.support.fakes.stub_volume_of import StubVolumeOf
from trashcli.list.main import ListCmd


class Tty(StringIO):
    def isatty(self):
        return True


class Pipe(StringIO):
    def isatty(self):
        return False


class TestTrashListSanitizesControlChars(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = MyPath.make_temp_dir()
        self.xdg_data_home = self.tmp_dir / 'xdg-data-home'
        info = self.xdg_data_home / 'Trash' / 'info'
        os.makedirs(info)
        # ESC is url-encoded as %1B in the stored Path=
        with open(info / 'evil.trashinfo', 'w') as f:
            f.write('[Trash Info]\n'
                    'Path=/tmp/danger%1B%5B31m\n'
                    'DeletionDate=2001-01-01T00:00:00\n')

    def _run(self, out):
        ListCmd(out=out, err=StringIO(),
                environ={'XDG_DATA_HOME': self.xdg_data_home},
                volumes_listing=FixedVolumesListing([]),
                uid=None, volumes=StubVolumeOf(),
                dir_reader=RealDirReader(),
                file_reader=RealTopTrashDirRulesReader(),
                content_reader=FileSystemContentReader(),
                version='0.0.0').run(['trash-list'])
        return out.getvalue()

    def test_on_a_terminal_the_escape_byte_is_removed(self):
        output = self._run(Tty())

        assert '\x1b' not in output
        assert '/tmp/danger' in output

    def test_when_piped_the_bytes_are_left_untouched(self):
        output = self._run(Pipe())

        assert '/tmp/danger\x1b[31m' in output

    def tearDown(self):
        self.tmp_dir.clean_up()
