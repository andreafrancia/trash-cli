import unittest

from trashcli.lib.print_version import PrintVersionArgs
from trashcli.restore.args import RunRestoreArgs
from trashcli.restore.restore_arg_parser import RestoreArgParser


class TestRestoreArgs(unittest.TestCase):
    def setUp(self):
        self.parser = RestoreArgParser()

    def test_default_path(self):
        args = self.parser.parse_restore_args([''], "curdir")

        self.assertEqual(RunRestoreArgs(path='curdir',
                                        sort='date',
                                        trash_dir=None,
                                        overwrite=False),
                         args)

    def test_path_specified_relative_path(self):
        args = self.parser.parse_restore_args(['', 'path'], "curdir")

        self.assertEqual(RunRestoreArgs(path='curdir/path',
                                        sort='date',
                                        trash_dir=None,
                                        overwrite=False),
                         args)

    def test_path_specified_fullpath(self):
        args = self.parser.parse_restore_args(['', '/a/path'], "ignored")

        self.assertEqual(RunRestoreArgs(path='/a/path',
                                        sort='date',
                                        trash_dir=None,
                                        overwrite=False),
                         args)

    def test_show_version(self):
        args = self.parser.parse_restore_args(['program', '--version'],
                                              "ignored")

        self.assertEqual(PrintVersionArgs(argv0='program'), args)
