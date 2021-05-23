import unittest

from six import StringIO

from tests.run_command import last_line_of


class TestTrashPutIssueMessage(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()

    def test_trash_empty_last_line(self):
        from trashcli.empty import EmptyCmd
        from trashcli.fs import FileSystemReader

        cmd = EmptyCmd(self.out, StringIO(), [], lambda:[],
                       now = None,
                       file_reader = FileSystemReader(),
                       getuid = None,
                       file_remover = None,
                       version = None,
                       )
        cmd.run('', '--help')

        self.assert_last_line_of_output_is(
                'Report bugs to https://github.com/andreafrancia/trash-cli/issues')

    def assert_last_line_of_output_is(self, expected):
        output = self.out.getvalue()
        last_line = last_line_of(output)
        assert expected == last_line, ('Last line of output should be:\n\n%s\n\n' % expected +
                      'but the output is\n\n%s' % output)
