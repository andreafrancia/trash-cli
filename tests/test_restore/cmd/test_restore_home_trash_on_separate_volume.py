from six import StringIO

from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.file_system import FakeReadCwd, FileReader
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trashed_files import TrashedFiles

HOME = '/home/user'
INFO = '/home/user/.local/share/Trash/info/report.trashinfo'


class FakeReader(FileReader):
    def __init__(self, contents):
        self.contents = contents

    def contents_of(self, path):
        return self.contents


class FakeSearcher:
    # the home trash lives on the /home volume, not on "/"
    def __init__(self, volume):
        self.volume = volume

    def all_file_in_info_dir(self, trash_dir_from_cli):
        from collections import namedtuple
        InfoFile = namedtuple('InfoFile', 'path type volume')
        yield InfoFile(INFO, 'trashinfo', self.volume)


class NullLogger:
    def warning(self, message):
        pass


class TestRestoreHomeTrashOnSeparateVolume:
    def run_restore_from(self, path, trashinfo, volume):
        stdout = StringIO()
        trashed_files = TrashedFiles(NullLogger(), FakeReader(trashinfo),
                                     FakeSearcher(volume))
        cmd = RestoreCmd.make(
            stdout=stdout, stderr=StringIO(), exit=lambda _: None,
            input=HardCodedInput(''), version="0.0.0",
            trashed_files=trashed_files, read_fs=None, write_fs=None,
            read_cwd=FakeReadCwd(path))
        cmd.run(['trash-restore', path])
        return stdout.getvalue()

    def test_an_absolute_home_entry_on_a_separate_home_volume_is_listed(self):
        trashinfo = ('[Trash Info]\n'
                     'Path=/home/user/report.txt\n'
                     'DeletionDate=2026-01-01T00:00:00\n')

        output = self.run_restore_from(HOME, trashinfo, volume='/home')

        assert '/home/user/report.txt' in output
