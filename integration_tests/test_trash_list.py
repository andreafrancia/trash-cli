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
        self.write_trashinfo(text("""\
            [TrashInfo]
            Path=/file1
            DeletionDate=2000-01-01T00:00:01
            """))
        self.write_trashinfo(text("""\
            [TrashInfo]
            Path=/file2
            DeletionDate=2000-01-01T00:00:02
            """))
        self.write_trashinfo(text("""\
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
        self.XDG_DATA_HOME = 'XDG_DATA_HOME'
        require_empty_dir(self.XDG_DATA_HOME)

        self.out = StringIO()
        self.number = 1

    def run(self):
        ListCmd(
            out = self.out,
            environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME}
        ).run()

    def assert_output_is(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.out.getvalue())

    def write_trashinfo(self, contents):
        write_file('%(XDG_DATA_HOME)s/Trash/info/%(name)s.trashinfo' % {
            'XDG_DATA_HOME' : self.XDG_DATA_HOME,
            'name' : str(self.number)}, contents)
        self.number = self.number + 1

class TestListCmd_list_files_from_other_trashcans:
    def test_something(self):
        self.write_trashinfo(text("""\
            [TrashInfo]
            Path=file1
            DeletionDate=2000-01-01T00:00:00
            """))

        self.out = StringIO()
        ListCmd(
            out          = self.out,
            environ      = {},
            getuid       = lambda: 123,
            list_volumes = lambda: ['.fake_root'],
        ).run()
        self.assert_output_is("2000-01-01 00:00:00 .fake_root/file1\n")

    def write_trashinfo(self, contents):
        self.number = 1
        write_file('%(trash_dir)s/info/%(name)s.trashinfo' % {
            'trash_dir' : '.fake_root/.Trash/123',
            'name' : str(self.number)}, contents)
        self.number = self.number + 1
    def assert_output_is(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.out.getvalue())

def text(string):
    result = ''
    for line in string.splitlines():
        result+=line.lstrip() + '\n'
    return result
