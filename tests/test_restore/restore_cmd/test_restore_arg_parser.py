import unittest

from trashcli.restore.parse_restore_args import parse_restore_args, \
    RunRestoreArgs, \
    PrintVersionArgs


class TestRestoreArgs(unittest.TestCase):
    def test_default_path(self):
        args = parse_restore_args([''], "curdir")

        self.assertEqual(RunRestoreArgs(path='curdir',
                                        sort='date',
                                        trash_dir=None,
                                        overwrite=False),
                         args)

    def test_path_specified_relative_path(self):
        args = parse_restore_args(['', 'path'], "curdir")

        self.assertEqual(RunRestoreArgs(path='curdir/path',
                                        sort='date',
                                        trash_dir=None,
                                        overwrite=False),
                         args)

    def test_path_specified_fullpath(self):
        args = parse_restore_args(['', '/a/path'], "ignored")

        self.assertEqual(RunRestoreArgs(path='/a/path',
                                        sort='date',
                                        trash_dir=None,
                                        overwrite=False),
                         args)

    def test_show_version(self):
        args = parse_restore_args(['program', '--version'], "ignored")

        self.assertEqual(PrintVersionArgs(action="TODO", argv0='program'), args)
