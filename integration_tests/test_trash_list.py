from trashcli.trash2 import ListCmd
from StringIO import StringIO
from files import write_file, require_empty_dir
from nose import SkipTest
from nose.tools import istest


@istest
class Describe_trash_list_output:
    @istest
    def should_output_the_help_message(self):
        self.run('trash-list', '--help')
        self.out.assert_equal_to("""\
Usage: trash-list [OPTIONS...]

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""")

    @istest
    def should_output_nothing_if_no_files(self):

        self.run()

        self.out.assert_equal_to('')

    @istest
    def should_output_deletion_date_and_path_of_trash(self):

        self.add_trashinfo('/aboslute/path', '2001-02-03T23:55:59')

        self.run()

        self.out.assert_equal_to( "2001-02-03 23:55:59 /aboslute/path\n")

    @istest
    def should_works_also_with_multiple_files(self):
        self.add_trashinfo("/file1", "2000-01-01T00:00:01")
        self.add_trashinfo("/file2", "2000-01-01T00:00:02")
        self.add_trashinfo("/file3", "2000-01-01T00:00:03")

        self.run()

        self.out.assert_equal_to( "2000-01-01 00:00:01 /file1\n"
                                  "2000-01-01 00:00:02 /file2\n"
                                  "2000-01-01 00:00:03 /file3\n")

    @istest
    def should_output_question_mark_if_deletion_date_is_not_present(self):
        self.info_dir.make_file('without-date.trashinfo', 
                ("[TrashInfo]\n"
                 "Path=/path\n"))
        self.run()
        self.out.assert_equal_to("????-??-?? ??:??:?? /path\n")

    @istest
    def should_output_question_marks_if_deletion_date_is_invalid(self):
        self.info_dir.make_file('without-date.trashinfo', 
                ("[TrashInfo]\n"
                 "Path=/path\n"
                 "DeletionDate=Wrong Date"))
        self.run()
        self.out.assert_equal_to("????-??-?? ??:??:?? /path\n")

    @istest
    def should_warn_about_empty_trashinfos(self):
        self.info_dir.touch('empty.trashinfo')

        self.run()

        self.err.assert_equal_to(
                "Parse Error: XDG_DATA_HOME/Trash/info/empty.trashinfo: "
                "Unable to parse Path\n")

    @istest
    def should_warn_about_unreadable_trashinfo(self):
        self.info_dir.make_unreadable_file('unreadable.trashinfo')

        self.run()

        self.err.assert_equal_to(
                "[Errno 13] Permission denied: "
                "'XDG_DATA_HOME/Trash/info/unreadable.trashinfo'\n")
    @istest
    def should_warn_about_unexistent_path_entry(self):
        def a_trashinfo_without_path():
            return ("[TrashInfo]\n"
                    "DeletionDate='2000-01-01T00:00:00'\n")
        self.info_dir.add_file(a_trashinfo_without_path())

        self.run()

        self.err.assert_equal_to(
                "Parse Error: XDG_DATA_HOME/Trash/info/1.trashinfo: "
                "Unable to parse Path\n")
        self.out.assert_equal_to('')

    def setUp(self):
        self.XDG_DATA_HOME = 'XDG_DATA_HOME'
        require_empty_dir( self.XDG_DATA_HOME)

        self.info_dir      = FakeInfoDir(self.XDG_DATA_HOME+'/Trash/info')
        self.add_trashinfo = self.info_dir.add_trashinfo

        self.out = OutputCollector()
        self.err = OutputCollector()


    def run(self, *argv):
        ListCmd(
            out = self.out,
            err = self.err,
            environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME}
        ).run(*argv)

@istest
class Describe_list_trash_on_volume_trashcans:
    @istest
    def should_list_method_1_trashcan_contents(self):
        self.method1.add_trashinfo('file1', '2000-01-01T00:00:00')

        self.run()

        self.out.assert_equal_to("2000-01-01 00:00:00 .fake_root/file1\n")

    @istest
    def should_list_method2_trashcan_contents(self):
        self.method2.add_trashinfo('file', '2000-01-01T00:00:00')

        self.run()

        self.out.assert_equal_to("2000-01-01 00:00:00 .fake_root/file\n")

    def setUp(self):
        self.fake_values = {'uid':123,
                            'topdir': '.fake_root'}

        require_empty_dir('.fake_root')

        self.method1 = FakeInfoDir( '%(topdir)s/.Trash/%(uid)s/info' %
                                    self.fake_values)

        self.method2 = FakeInfoDir( '%(topdir)s/.Trash-%(uid)s/info' %
                                    self.fake_values)

    def run(self, *argv):
        self.out = OutputCollector()
        ListCmd(
            out = self.out,
            err = StringIO(),
            environ = {},
            getuid       = lambda: self.fake_values.get('uid'),
            list_volumes = lambda: [self.fake_values.get('topdir')],
        ).run(*argv)

class FakeInfoDir:
    def __init__(self, path):
        self.path = path
        self.number = 1
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
        return os.path.join(self.path, path_relative_to_info_dir)
    def add_file(self, contents):
        path = '%(info_dir)s/%(name)s.trashinfo' % { 'info_dir' : self.path,
                                                     'name' : str(self.number)}
        write_file(path, contents)

        self.number = self.number + 1
        self.path_of_last_file_added = path

    def add_trashinfo(self, escaped_path_entry, formatted_deletion_date):
        self.add_file(trashinfo(escaped_path_entry, formatted_deletion_date))

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

