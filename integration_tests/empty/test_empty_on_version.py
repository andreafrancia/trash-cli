import unittest
from textwrap import dedent

from six import StringIO

from integration_tests.empty import no_volumes
from trashcli.empty import EmptyCmd
from trashcli.fs import FileSystemReader


class TestEmpty_on_version(unittest.TestCase):
    def test_it_print_version(self):
        err, out = StringIO(), StringIO()
        cmd = EmptyCmd(err = err,
                       out = out,
                       environ = {},
                       list_volumes = no_volumes,
                       now = None,
                       file_reader = FileSystemReader(),
                       getuid = None,
                       file_remover = None,
                       version = '1.2.3',
                       )
        cmd.run('trash-empty', '--version')
        assert out.getvalue() == dedent("""\
            trash-empty 1.2.3
            """)
