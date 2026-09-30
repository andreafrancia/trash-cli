from trashcli.lib.print_version import PrintVersionArgs
from trashcli.restore.args import RunRestoreArgs, Sort
from trashcli.restore.restore_arg_parser import RestoreArgParser


class TestRestoreArgs:
    def setup_method(self):
        self.parser = RestoreArgParser()

    def test_default_path(self):
        args = self.parser.parse_restore_args([''], "curdir")

        assert args == RunRestoreArgs(path='curdir',
                                      sort=Sort.ByDate,
                                      trash_dir=None,
                                      overwrite=False)

    def test_path_specified_relative_path(self):
        args = self.parser.parse_restore_args(['', 'path'], "curdir")

        assert args == RunRestoreArgs(path='curdir/path',
                                      sort=Sort.ByDate,
                                      trash_dir=None,
                                      overwrite=False)

    def test_path_specified_fullpath(self):
        args = self.parser.parse_restore_args(['', '/a/path'], "ignored")

        assert args == RunRestoreArgs(path='/a/path',
                                      sort=Sort.ByDate,
                                      trash_dir=None,
                                      overwrite=False)

    def test_show_version(self):
        args = self.parser.parse_restore_args(['program', '--version'],
                                              "ignored")

        assert args == PrintVersionArgs(argv0='program')
