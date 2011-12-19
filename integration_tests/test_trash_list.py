# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash2 import ListCmd
from trashcli.trash  import has_sticky_bit
from StringIO import StringIO
from files import write_file, require_empty_dir, make_sticky_dir
from nose.tools import istest

@istest
class Describe_trash_list_output:
    @istest
    def should_output_the_help_message(self):
        self.run('trash-list', '--help')
        self.output_should_be("""\
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

        self.output_should_be('')

    @istest
    def should_output_deletion_date_and_path_of_trash(self):

        self.add_trashinfo('/aboslute/path', '2001-02-03T23:55:59')

        self.run()

        self.output_should_be( "2001-02-03 23:55:59 /aboslute/path\n")

    @istest
    def should_works_also_with_multiple_files(self):
        self.add_trashinfo("/file1", "2000-01-01T00:00:01")
        self.add_trashinfo("/file2", "2000-01-01T00:00:02")
        self.add_trashinfo("/file3", "2000-01-01T00:00:03")

        self.run()

        self.output_should_be( "2000-01-01 00:00:01 /file1\n"
                                  "2000-01-01 00:00:02 /file2\n"
                                  "2000-01-01 00:00:03 /file3\n")

    @istest
    def should_output_question_mark_if_deletion_date_is_not_present(self):
        self.info_dir.make_file('without-date.trashinfo', 
                ("[TrashInfo]\n"
                 "Path=/path\n"))
        self.run()
        self.output_should_be("????-??-?? ??:??:?? /path\n")

    @istest
    def should_output_question_marks_if_deletion_date_is_invalid(self):
        self.info_dir.make_file('without-date.trashinfo', 
                ("[TrashInfo]\n"
                 "Path=/path\n"
                 "DeletionDate=Wrong Date"))
        self.run()
        self.output_should_be("????-??-?? ??:??:?? /path\n")

    @istest
    def should_warn_about_empty_trashinfos(self):
        self.info_dir.touch('empty.trashinfo')

        self.run()

        self.error_should_be(
                "Parse Error: XDG_DATA_HOME/Trash/info/empty.trashinfo: "
                "Unable to parse Path\n")

    @istest
    def should_warn_about_unreadable_trashinfo(self):
        self.info_dir.make_unreadable_file('unreadable.trashinfo')

        self.run()

        self.error_should_be(
                "[Errno 13] Permission denied: "
                "'XDG_DATA_HOME/Trash/info/unreadable.trashinfo'\n")
    @istest
    def should_warn_about_unexistent_path_entry(self):
        def a_trashinfo_without_path():
            return ("[TrashInfo]\n"
                    "DeletionDate='2000-01-01T00:00:00'\n")
        self.info_dir.add_file(a_trashinfo_without_path())

        self.run()

        self.error_should_be(
                "Parse Error: XDG_DATA_HOME/Trash/info/1.trashinfo: "
                "Unable to parse Path\n")
        self.output_should_be('')

    def setUp(self):
        self.XDG_DATA_HOME = 'XDG_DATA_HOME'
        require_empty_dir( self.XDG_DATA_HOME)

        self.info_dir      = FakeInfoDir(self.XDG_DATA_HOME+'/Trash/info')
        self.add_trashinfo = self.info_dir.add_trashinfo

        runner = TrashListRunner( environ = {'XDG_DATA_HOME': self.XDG_DATA_HOME})
        self.output_should_be = runner.output_should_be
        self.error_should_be  = runner.error_should_be
        self.run = runner

@istest
class describe_list_trash_with_top_trash_directory_type_1:
    @istest
    def should_list_method_1_trashcan_contents(self):
        make_sticky_dir('topdir/.Trash')
        trashdir = FakeInfoDir('topdir/.Trash/123/info')
        trashdir.add_trashinfo('file1', '2000-01-01T00:00:00')

        self.run()

        self.output_should_be("2000-01-01 00:00:00 topdir/file1\n")

    @istest
    def should_ignore_contents_when_is_not_sticky(self):
        trashdir = FakeInfoDir('topdir/.Trash/123/info')
        trashdir.add_trashinfo('file1', '2000-01-01T00:00:00')
        ensure_non_sticky_dir('topdir/.Trash')

        self.run()

        self.output_should_be("")

    @istest
    def should_list_method2_trashcan_contents(self):
        trashdir = FakeInfoDir('topdir/.Trash-123/info')
        trashdir.add_trashinfo('file', '2000-01-01T00:00:00')

        self.run()

        self.output_should_be("2000-01-01 00:00:00 topdir/file\n")

    def setUp(self):
        require_empty_dir('topdir')

        runner = TrashListRunner()
        runner.set_fake_uid(123)
        runner.add_volume('topdir')

        self.run = runner
        self.output_should_be = runner.output_should_be

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

def ensure_non_sticky_dir(path):
    import os
    assert os.path.isdir(path)
    assert not has_sticky_bit(path)

class TrashListRunner:
    def __init__(self, environ={}):
        self.stdout      = OutputCollector()
        self.stderr      = OutputCollector()
        self.environ     = environ
        self.fake_getuid = self.error
        self.volumes     = []
    def __call__(self, *argv):
        self.run(argv)
    def run(self,argv):
        ListCmd(
            out = self.stdout,
            err = self.stderr,
            environ = self.environ,
            getuid = self.fake_getuid,
            list_volumes = lambda: self.volumes
        ).run(*argv)
    def set_fake_uid(self, uid):
        self.fake_getuid = lambda: uid
    def add_volume(self, mount_point):
        self.volumes.append(mount_point)
    def error(self):
        raise ValueError()
    def output_should_be(self, expected_value):
        self.stdout.assert_equal_to(expected_value)
    def error_should_be(self, expected_value):
        self.stderr.assert_equal_to(expected_value)

class OutputCollector:
    def __init__(self):
        self.stream = StringIO()
    def write(self,data):
        self.stream.write(data)
    def assert_equal_to(self, expected):
        return self.should_be(expected)
    def should_be(self, expected):
        from assert_equals_with_unidiff import assert_equals_with_unidiff
        assert_equals_with_unidiff(expected, self.stream.getvalue())
    def getvalue(self):
        return self.stream.getvalue()
    def assert_matches(self, regex):
        text = self.stream.getvalue()
        from nose.tools import assert_regexp_matches
        assert_regexp_matches(text, regex)

