from six import StringIO

from tests.support.py2mock import Mock
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.file_system import FakeReadCwd
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.trashed_file import TrashedFile
from trashcli.restore.trashed_files import TrashedFiles


class TestRestoreSortAndMissingDate:
    def setup_method(self):
        self.stdout = StringIO()
        self.trashed_files = Mock(spec=TrashedFiles)
        self.cmd = RestoreCmd.make(
            stdout=self.stdout, stderr=StringIO(), exit=lambda _: None,
            input=HardCodedInput(''), version="0.0.0",
            trashed_files=self.trashed_files, read_fs=Mock(spec=[]),
            write_fs=Mock(spec=[]), read_cwd=FakeReadCwd("/home/u"))

    def given_trashed_files(self, *files):
        # a generator, like the real collaborator, to catch re-iteration bugs
        self.trashed_files.all_trashed_files = \
            lambda _path=None: (f for f in files)

    def run_restore(self, *args):
        self.cmd.run(['trash-restore'] + list(args))
        return self.stdout.getvalue()

    def test_sort_none_lists_without_crashing(self):
        self.given_trashed_files(a_trashed_file("/home/u/a", dated('2020-01-01')))

        assert '/home/u/a' in self.run_restore('--sort=none')

    def test_a_missing_date_does_not_crash_the_default_sort(self):
        self.given_trashed_files(a_trashed_file("/home/u/a", None),
                                 a_trashed_file("/home/u/b", dated('2020-01-01')))

        assert '/home/u/a' in self.run_restore()

    def test_a_missing_date_is_listed_with_a_placeholder(self):
        self.given_trashed_files(a_trashed_file("/home/u/a", None))

        assert '????-??-?? ??:??:?? /home/u/a' in self.run_restore()


def dated(text):
    import datetime
    return datetime.datetime.strptime(text, '%Y-%m-%d')


def a_trashed_file(original_location, deletion_date):
    return TrashedFile(original_location=original_location,
                       deletion_date=deletion_date,
                       info_file="/info", original_file="/orig")
