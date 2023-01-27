import unittest

from trashcli.restore.parse_restore_args import parse_restore_args
from trashcli.restore.parse_restore_args import Command


class Test_parse_args(unittest.TestCase):
    def test_default_path(self):
        args = parse_restore_args([''], "curdir")

        self.assertEqual((Command.RunRestore,
                          {'path': 'curdir',
                           'sort': 'date',
                           'trash_dir': None,
                           'overwrite': False}),
                         args)

    def test_path_specified_relative_path(self):
        args = parse_restore_args(['', 'path'], "curdir")

        self.assertEqual((Command.RunRestore,
                          {'path': 'curdir/path',
                           'sort': 'date',
                           'trash_dir': None,
                           'overwrite': False}),
                         args)

    def test_path_specified_fullpath(self):
        args = parse_restore_args(['', '/a/path'], "ignored")

        self.assertEqual((Command.RunRestore,
                          {'path': '/a/path',
                           'sort': 'date',
                           'trash_dir': None,
                           'overwrite': False}),
                         args)

    def test_show_version(self):
        args = parse_restore_args(['', '--version'], "ignored")

        self.assertEqual((Command.PrintVersion, None), args)
