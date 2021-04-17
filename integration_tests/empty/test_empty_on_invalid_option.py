import unittest
from textwrap import dedent

from six import StringIO

from integration_tests.empty import no_volumes
from trashcli.empty import EmptyCmd
from trashcli.fs import FileSystemReader


class TestEmpty_on_invalid_option(unittest.TestCase):
    def setUp(self):
        self.err, self.out = StringIO(), StringIO()
        self.cmd = EmptyCmd(
            err=self.err,
            out=self.out,
            environ={},
            list_volumes=no_volumes,
            now=None,
            file_reader=FileSystemReader(),
            getuid=None,
            file_remover=None,
            version=None,
        )

    def test_it_should_fail(self):
        self.exit_code = self.cmd.run('trash-empty', '-2')

        exit_code_for_command_line_usage = 64
        assert exit_code_for_command_line_usage == self.exit_code

    def test_it_should_complain_to_the_standard_error(self):
        self.exit_code = self.cmd.run('trash-empty', '-2')

        assert self.err.getvalue() == dedent("""\
                trash-empty: invalid option -- '2'
                """)

    def test_with_a_different_option(self):
        self.cmd.run('trash-empty', '-3')

        assert self.err.getvalue() == dedent("""\
                trash-empty: invalid option -- '3'
                """)
