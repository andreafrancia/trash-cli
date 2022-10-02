import unittest

from trashcli import restore
from trashcli.restore import Command


class Test_parse_args(unittest.TestCase):
    def test_default_path(self):
        args = restore.parse_args([''], "curdir")

        self.assertEqual((Command.RunRestore,
                          {'path': 'curdir',
                           'sort': 'date',
                           'trash_dir': None}),
                         args)

    def test_path_specified_relative_path(self):
        args = restore.parse_args(['', 'path'], "curdir")

        self.assertEqual((Command.RunRestore,
                          {'path': 'curdir/path',
                           'sort': 'date',
                           'trash_dir': None}),
                         args)

    def test_path_specified_fullpath(self):
        args = restore.parse_args(['', '/a/path'], "ignored")

        self.assertEqual((Command.RunRestore,
                          {'path': '/a/path',
                           'sort': 'date',
                           'trash_dir': None}),
                         args)

    def test_show_version(self):
        args = restore.parse_args(['', '--version'], "ignored")

        self.assertEqual((Command.PrintVersion, None), args)
