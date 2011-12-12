from trashcli.trash2 import ListCmd
from StringIO import StringIO
from files import write_file, require_empty_dir
from nose import SkipTest

class TestListCmd_should_list_files:
    def test_when_there_are_no_files(self):

        self.run()

        self.out.assert_equal_to('')

    def test_when_there_is_one_file(self):

        self.add_trashinfo('/aboslute/path', '2001-02-03T23:55:59')

        self.run()

        self.out.assert_equal_to( "2001-02-03 23:55:59 /aboslute/path\n")

    def test_when_there_are_multiple_files(self):
        self.add_trashinfo("/file1", "2000-01-01T00:00:01")
        self.add_trashinfo("/file2", "2000-01-01T00:00:02")
        self.add_trashinfo("/file3", "2000-01-01T00:00:03")

        self.run()

        self.out.assert_equal_to( "2000-01-01 00:00:01 /file1\n"
                                  "2000-01-01 00:00:02 /file2\n"
                                  "2000-01-01 00:00:03 /file3\n")

    def test_it_should_warn_on_badly_formatted_trashinfo(self):
        self.info_dir.touch('empty.trashinfo')

        self.run()

        self.out.assert_equal_to('')
        self.err.assert_equal_to(
                "Parse Error: XDG_DATA_HOME/Trash/info/empty.trashinfo: "
                "Unable to parse Path\n")

    def test_it_should_warn_on_unreadable_trashinfo(self):
        self.info_dir.make_unreadable_file('unreadable.trashinfo')

        self.run()

        self.out.assert_equal_to('')
        self.err.assert_equal_to(
                "[Errno 13] Permission denied: "
                "'XDG_DATA_HOME/Trash/info/unreadable.trashinfo'\n")

    def test_it_shows_help_message(self):
        self.run('trash-list', '--help')
        self.out.assert_equal_to("""\
Usage: trash-list [OPTIONS...]

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""")
        self.err.assert_equal_to('')

    def test_it_shows_files_even_also_deletion_date_is_unparsable(self):
        self.info_dir.make_file('without-date.trashinfo', 
                ("[TrashInfo]\n"
                 "Path=/path\n"))
        self.run()
        self.err.assert_equal_to('')
        self.out.assert_equal_to("????-??-?? ??:??:?? /path\n")

    def setUp(self):
        self.XDG_DATA_HOME = 'XDG_DATA_HOME'

        require_empty_dir(self.XDG_DATA_HOME)
        self.fake_info_dir = FakeInfoDir(self.XDG_DATA_HOME+'/Trash/info')
        self.add_trashinfo = self.fake_info_dir.add_trashinfo

        self.out = OutputCollector()
        self.err = OutputCollector()

        class InfoDir:
            def __init__(self, XDG_DATA_HOME):
                self.XDG_DATA_HOME = XDG_DATA_HOME
            def make_file(self, path_relative_to_info_dir, contents):
                path = self.real_path(path_relative_to_info_dir)
                write_file(path, contents)
            def touch(self, path_relative_to_info_dir):
                self.make_file(path_relative_to_info_dir, '')
            def make_unreadable_file(self, path_relative_to_info_dir):
                path = self.real_path(path_relative_to_info_dir)
                make_unreadable_file(path)
            def real_path(self, path_relative_to_info_dir):
                import os
                path = os.path.join(self.XDG_DATA_HOME, 'Trash', 'info',
                                    path_relative_to_info_dir)
                return path

        self.info_dir = InfoDir(self.XDG_DATA_HOME)

    def run(self, *argv):
        ListCmd(
            out = self.out,
            err = self.err,
            environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME}
        ).run(*argv)

def make_unreadable_file(path):
    write_file(path, '')
    import os
    os.chmod(path, 0)
    from nose.tools import assert_raises
    with assert_raises(IOError):
        file(path).read()

def trashinfo(escaped_path_entry, formatted_deletion_date):
    return ("[TrashInfo]\n" + 
            "Path=%s\n" % escaped_path_entry + 
            "DeletionDate=%s\n" % formatted_deletion_date)

class TestListCmd_with_volume_trashcans:
    def setUp(self):
        self.fake_uid = 123
        self.fake_volume = '.fake_root'

        require_empty_dir(self.fake_volume)

        self.fake_info_dir1 = FakeInfoDir(
                '%(volume)s/.Trash/%(uid)s/info' % {
                    'volume' : self.fake_volume,
                    'uid'    : self.fake_uid})

        self.fake_info_dir2 = FakeInfoDir(
                '%(volume)s/.Trash-%(uid)s/info' % {
                    'volume' : self.fake_volume,
                    'uid'    : self.fake_uid})

    def test_it_lists_trash_from_method1_trashcan(self):
        self.fake_info_dir1.add_trashinfo('file1', '2000-01-01T00:00:00')

        self.out = OutputCollector()
        ListCmd(
            out          = self.out,
            err          = StringIO(),
            environ      = {},
            getuid       = lambda: 123,
            list_volumes = lambda: ['.fake_root'],
        ).run()

        self.out.assert_equal_to("2000-01-01 00:00:00 .fake_root/file1\n")

    def test_it_lists_trash_from_method2_trashcan(self):
        self.fake_info_dir2.add_trashinfo('file', '2000-01-01T00:00:00')

        self.out = OutputCollector()
        ListCmd(
            out          = self.out,
            err          = StringIO(),
            environ      = {},
            getuid       = lambda: 123,
            list_volumes = lambda: ['.fake_root'],
        ).run()

        self.out.assert_equal_to("2000-01-01 00:00:00 .fake_root/file\n")


class OutputCollector:
    def __init__(self):
        self.stream = StringIO()
    def write(self,data):
        self.stream.write(data)
    def assert_equal_to(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.stream.getvalue())
    def getvalue(self):
        return self.stream.getvalue()
    def assert_matches(self, regex):
        text = self.stream.getvalue()
        from nose.tools import assert_regexp_matches
        assert_regexp_matches(text, regex)

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

