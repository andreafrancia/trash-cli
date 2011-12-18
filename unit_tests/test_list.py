# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from nose.tools import assert_equals
from trashcli.trash import List

from StringIO import StringIO
import unittest
class TestList_on_help(unittest.TestCase):
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

