from trashcli.trash2 import ListCmd
from StringIO import StringIO
from files import write_file, require_empty_dir

class TestListCmd_removes_files:

    def test_it_should_print_nothing_on_no_trashed_files(self):
        
        self.run()

        self.assert_output_is('')

    def test_it_should_print_date_and_time_the_path(self):
        write_file('XDG_DATA_HOME/Trash/info/foo.trashinfo', text("""\
                   [TrashInfo]
                   Path=/aboslute/path/to/the/file
                   DeletionDate=2001-02-03T23:55:59
                   """))
        self.run()

        self.assert_output_is("""\
2001-02-03 23:55:59 /aboslute/path/to/the/file
""")

    def setUp(self):
        require_empty_dir('XDG_DATA_HOME')
        self.out = StringIO()

    def run(self):
        ListCmd(
            out = self.out,
            environ = {'XDG_DATA_HOME': 'XDG_DATA_HOME'}
        ).run()

    def assert_output_is(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.out.getvalue())

def text(string):
    result = ''
    for line in string.splitlines():
        result+=line.lstrip() + '\n'
    return result
