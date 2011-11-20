from nose.tools import assert_equals
from trashcli.trash import List

from StringIO import StringIO
import unittest
class DontTestList(unittest.TestCase):
    def test_help_option(self):
        out=StringIO()
        cmd=List(out)
        cmd.main('trash-list', '--help')
        assert_equals(out.getvalue(), """\
Usage: trash-list

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""")

    def test_list(self):
        out=StringIO()
        cmd=List(out)
        cmd.main('trash-list')
        assert_equals(out.getvalue(), """\
2011-11-20 20:53:20 /Users/andreafrancia/trash-cli_svn2git/ciao
2011-11-20 20:53:26 /Users/andreafrancia/trash-cli_svn2git/ciao2
""")
