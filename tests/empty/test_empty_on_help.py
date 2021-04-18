import unittest
from textwrap import dedent

import pytest
import six
from six import StringIO

from . import no_volumes
from trashcli.empty import EmptyCmd
from trashcli.fs import FileSystemReader


@pytest.mark.slow
class TestTrashEmpty_on_help(unittest.TestCase):
    def setUp(self):
        self.err, self.out = StringIO(), StringIO()
        self.cmd = EmptyCmd(err=self.err,
                       out=self.out,
                       environ={},
                       list_volumes=no_volumes,
                       now=None,
                       file_reader=FileSystemReader(),
                       getuid=None,
                       file_remover=None,
                       version=None,
                       )

    def test_help_output(self):

        self.cmd.run('trash-empty', '--help')

        assert self.out.getvalue() == dedent("""\
            Usage: trash-empty [days]

            Purge trashed files.

            Options:
              --version   show program's version number and exit
              -h, --help  show this help message and exit

            Report bugs to https://github.com/andreafrancia/trash-cli/issues
            """)

    def test(self):

        self.cmd.run('trash-empty', '-h')

        six.assertRegex(self, self.out.getvalue(), '^Usage. trash-empty.*')
