import unittest

from trashcli.empty import parse_argv


class TestParser(unittest.TestCase):

    def test_argument_option_called_without_argument(self):
        result = parse_argv(['--trash-dir'])

        assert result == ('invalid_option', ('trash-dir',))

    def test_argument_option_called_with_argument(self):
        result = parse_argv(['--trash-dir', 'trash-dir1'])

        assert result == ('default', (False, ['trash-dir1'], None))

    def test_all_user_trash_dirs(self):
        result = parse_argv(['--all-users'])

        assert result == ('default', (True, [], None))

    def test_argument_option_called_with_argument2(self):
        result = parse_argv(['--trash-dir=trash-dir1'])

        assert result == ('default', (False, ['trash-dir1'], None))

    def test_argument_option_called_with_argument3(self):
        result = parse_argv(['--trash-dir', 'trash-dir1'])

        assert result == ('default', (False, ['trash-dir1'], None))

    def test_it_calls_help(self):
        result = parse_argv(['--help'])

        assert result == ('print_help', ())

    def test_how_getopt_works_with_an_invalid_option(self):
        result = parse_argv(['-x'])

        assert result == ('invalid_option', ('x',))

    def test_on_argument(self):
        result = parse_argv(['1'])

        assert result == ('default', (False, [], 1))

    def test_on_help(self):
        result = parse_argv(['--help'])

        assert result == ('print_help', ())

    def test_trash_dir_multiple_days(self):
        result = parse_argv(['--trash-dir', 'one',
                            '--trash-dir', 'two'])

        assert result == ('default', (False, ['one', 'two'], None))
