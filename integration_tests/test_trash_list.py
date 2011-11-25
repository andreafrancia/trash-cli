from trashcli.trash2 import ListCmd
from StringIO import StringIO
from files import write_file, require_empty_dir

class TestListCmd_should_list_files:

    def test_when_there_are_no_files(self):
        
        self.run()

        self.assert_output_is('')

    def test_when_there_is_one_file(self):
        write_file('XDG_DATA_HOME/Trash/info/foo.trashinfo', text("""\
            [TrashInfo]
            Path=/aboslute/path/to/the/file
            DeletionDate=2001-02-03T23:55:59
            """))
        self.run()

        self.assert_output_is(
            "2001-02-03 23:55:59 /aboslute/path/to/the/file\n")

    def test_when_there_are_multiple_files(self):
        write_file('XDG_DATA_HOME/Trash/info/file1.trashinfo', text("""\
            [TrashInfo]
            Path=/file1
            DeletionDate=2000-01-01T00:00:01
            """))
        write_file('XDG_DATA_HOME/Trash/info/file2.trashinfo', text("""\
            [TrashInfo]
            Path=/file2
            DeletionDate=2000-01-01T00:00:02
            """))
        write_file('XDG_DATA_HOME/Trash/info/file3.trashinfo', text("""\
            [TrashInfo]
            Path=/file3
            DeletionDate=2000-01-01T00:00:03
            """))
        self.run()

        self.assert_output_is(
            "2000-01-01 00:00:01 /file1\n"
            "2000-01-01 00:00:02 /file2\n"
            "2000-01-01 00:00:03 /file3\n"
        )

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
