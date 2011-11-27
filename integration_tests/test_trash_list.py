from trashcli.trash2 import ListCmd
from StringIO import StringIO
from files import write_file, require_empty_dir

class TestListCmd_should_list_files:
    def test_when_there_are_no_files(self):
        
        self.run()

        self.assert_output_is('')

    def test_when_there_is_one_file(self):

        self.add_trashinfo('/aboslute/path', '2001-02-03T23:55:59')

        self.run()

        self.assert_output_is( "2001-02-03 23:55:59 /aboslute/path\n")

    def test_when_there_are_multiple_files(self):
        self.add_trashinfo("/file1", "2000-01-01T00:00:01")
        self.add_trashinfo("/file2", "2000-01-01T00:00:02")
        self.add_trashinfo("/file3", "2000-01-01T00:00:03")

        self.run()

        self.assert_output_is( "2000-01-01 00:00:01 /file1\n"
                               "2000-01-01 00:00:02 /file2\n"
                               "2000-01-01 00:00:03 /file3\n")

    def setUp(self):
        self.XDG_DATA_HOME = 'XDG_DATA_HOME'
        require_empty_dir(self.XDG_DATA_HOME)
        self.fake_info_dir = FakeInfoDir(self.XDG_DATA_HOME+'/Trash/info')

        self.output_collector = StringIO()

    def run(self):
        ListCmd(
            out = self.output_collector,
            environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME}
        ).run()

    def assert_output_is(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.actual_output())

    def actual_output(self):
        return self.output_collector.getvalue()

    def add_trashinfo(self, escaped_path_entry,
                            formatted_deletion_date):
        self.fake_info_dir.add_trashinfo(escaped_path_entry,
                                         formatted_deletion_date)
class FakeInfoDir:
    def __init__(self, path):
        self.path   = path
        self.number = 1

    def add_file(self, contents):
        write_file('%(info_dir)s/%(name)s.trashinfo' % {
            'info_dir' : self.path,
            'name' : str(self.number)}, contents)
        self.number = self.number + 1
    def add_trashinfo(self, escaped_path_entry, formatted_deletion_date):
        self.add_file(trashinfo(escaped_path_entry, formatted_deletion_date))
def trashinfo(escaped_path_entry, formatted_deletion_date):
    return ("[TrashInfo]\n" + 
            "Path=%s\n" % escaped_path_entry + 
            "DeletionDate=%s\n" % formatted_deletion_date)

class TestListCmd_list_files_from_other_trashcans:
    def setUp(self):
        self.fake_uid = 123
        self.fake_volume = '.fake_root'

        require_empty_dir(self.fake_volume)

        self.fake_info_dir = FakeInfoDir(
                '%(volume)s/.Trash/%(uid)s/info' % {
                    'volume' : self.fake_volume,
                    'uid'    : self.fake_uid})

    def test_something(self):
        self.add_trashinfo('file1', '2000-01-01T00:00:00')

        self.out = StringIO()
        ListCmd(
            out          = self.out,
            environ      = {},
            getuid       = lambda: 123,
            list_volumes = lambda: ['.fake_root'],
        ).run()

        self.assert_output_is("2000-01-01 00:00:00 .fake_root/file1\n")

    def add_trashinfo(self, escaped_path_entry,
                            formatted_deletion_date):
        self.fake_info_dir.add_trashinfo(escaped_path_entry, 
                                         formatted_deletion_date)

    def assert_output_is(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.out.getvalue())

