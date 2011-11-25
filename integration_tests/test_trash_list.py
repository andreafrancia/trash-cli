from trashcli.trash2 import ListCmd
from nose.tools import assert_equals
from assert_equals_with_unidiff import assert_equals_with_unidiff
from nose import SkipTest
from StringIO import StringIO
from files import write_file, require_empty_dir

class TestListCmd_removes_files:
    def test_it_should_print_nothing_on_no_trashed_files(self):
        out = StringIO()
        ListCmd(
            out = out,
            environ = {}
        ).run()
        assert_equals_with_unidiff('', out.getvalue())
    def test_it_should_print_date_and_time_the_path(self):
        require_empty_dir('XDG_DATA_HOME')

        write_file('XDG_DATA_HOME/Trash/info/foo.trashinfo', """\
[TrashInfo]
Path=/aboslute/path/to/the/file
DeletionDate=2001-02-03T23:55:59
""")
        out = StringIO()
        ListCmd(
            out = out,
            environ = {'XDG_DATA_HOME': 'XDG_DATA_HOME'}
        ).run()
        assert_equals_with_unidiff("""\
2001-02-03 23:55:59 /aboslute/path/to/the/file
""", out.getvalue())
