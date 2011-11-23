from nose.tools import assert_equals
from trashcli.trash2 import read_deletion_date, EmptyCmd

def test_how_to_parse_date_from_trashinfo():
    from datetime import datetime
    assert_equals(datetime(2000,12,31,23,59,58), read_deletion_date('DeletionDate=2000-12-31T23:59:58'))
    assert_equals(datetime(2000,12,31,23,59,58), read_deletion_date('DeletionDate=2000-12-31T23:59:58\n'))
    assert_equals(datetime(2000,12,31,23,59,58), read_deletion_date('[TrashInfo]\nDeletionDate=2000-12-31T23:59:58'))


from trashcli.trash2 import InfoDirs
class TestInfoDirsPathsFrom():
    def test_no_path_if_no_environment_variables(self):
        self.with_environ({})
        self.should_return([])
    def test_it_honours_the_xdg_datahome(self):
        self.with_environ({'XDG_DATA_HOME':'/alternate/xdg/data/home'})
        self.should_return(['/alternate/xdg/data/home/Trash/info'])
    def test_it_uses_the_default_value_of_xdg_datahome(self):
        self.with_environ({'HOME':'/home/foo'})
        self.should_return(['/home/foo/.local/share/Trash/info'])

    def test_it_considers_trashcans_volumes(self):
        self.with_volumes('/mnt')
        self.with_user_id('123')
        self.should_return(['/mnt/Trash/123/info',
                            '/mnt/Trash-123/info'])

    def with_environ(self, environ):
        self.environ = environ
    def with_volumes(self, *volumes_paths):
        self.list_volumes = lambda:volumes_paths
    def with_user_id(self, uid):
        self.getuid = lambda: uid
    def should_return(self, expected_result):
        result = InfoDirs(environ      = self.environ,
                          getuid       = self.getuid,
                          list_volumes = self.list_volumes).paths()
        assert_equals(expected_result, list(result))
    def setUp(self):
        self.environ      = {}
        self.getuid       = lambda:None
        self.list_volumes = lambda:[]

from trashcli.trash2 import InfoDir
class TestInfoDir:
    def test(self):
        self.result=[]
        self.fs = FakeFileSystem()
        self.fs.create_fake_file('/info/foo.trashinfo')
        self.infodir=InfoDir(self.fs, '/info')
        self.infodir.for_all_orphan(self.result.append)

        assert_equals([], self.result)
    def test2(self):
        self.result=[]
        self.fs = FakeFileSystem()
        self.fs.create_fake_file('/files/foo')
        self.infodir=InfoDir(self.fs, '/info')
        self.infodir.for_all_orphan(self.result.append)

        assert_equals(['/files/foo'], self.result)


class FakeFileSystem:
    def __init__(self):
        self.files={}
        self.dirs={}
        self.deleted=[]
    def contents_of(self, path):
        return self.files[path]
    def remove_file(self, path):
        self.deleted.append(path)
        return
    def exists(self, path):
        return path in self.files
    def entries_if_dir_exists(self, path):
        return self.dirs.get(path, [])
    def create_fake_file(self, path, contents=''):
        import os
        self.files[path] = contents
        self.create_fake_dir(os.path.dirname(path), os.path.basename(path))
    def create_fake_dir(self, dir_path, *dir_entries):
        self.dirs[dir_path] = dir_entries
    def removed_files(self):
        return self.deleted[:]

class TestFakeFileSystem:
    def setUp(self):
        self.fs = FakeFileSystem()
    def test_you_can_read_from_files(self):
        self.fs.create_fake_file('/path/to/file', "file contents")
        assert_equals('file contents', self.fs.contents_of('/path/to/file'))
    def test_when_creating_a_fake_file_it_creates_also_the_dir(self):
        self.fs.create_fake_file('/dir/file')
        assert_equals(set(('file',)), set(self.fs.entries_if_dir_exists('/dir')))
    def test_you_can_create_multiple_fake_file(self):
        self.fs.create_fake_file('/path/to/file1', "one")
        self.fs.create_fake_file('/path/to/file2', "two")
        assert_equals('one', self.fs.contents_of('/path/to/file1'))
        assert_equals('two', self.fs.contents_of('/path/to/file2'))
    def test_no_file_exists_at_beginning(self):
        assert not self.fs.exists('/filename')
    def test_after_a_creation_the_file_exists(self):
        self.fs.create_fake_file('/filename')
        assert self.fs.exists('/filename')
    def test_create_fake_dir(self):
        self.fs.create_fake_dir('/etc', 'passwd', 'shadow', 'hosts')
        
        assert_equals(set(['passwd', 'shadow', 'hosts']),
                      set(self.fs.entries_if_dir_exists('/etc')))
    def test_it_keeps_track_of_deleted_files(self):
        self.fs.remove_file('the-first-file-being-deleted')
        self.fs.remove_file('the-second-one')

        assert_equals(['the-first-file-being-deleted',
                       'the-second-one'], self.fs.removed_files())

from StringIO import StringIO
from nose import SkipTest
class TestEmptyCmdWithMultipleVolumes:
    def test_it_removes_trashinfos_from_method_1_dir(self):
        class Fake:
            def entries_if_dir_exists(self,path):
                return ['foo.trashinfo']
            def contents_of(self, path):
                return ''
            def remove_file_if_exists(self,path):
                pass
            def remove_file(self,path):
                pass
            pass
        fs=Fake()

        raise SkipTest()
        from trashcli.trash2 import InfoDir
        infodir=InfoDir(fs, '/mnt/.Trash/123/info')

        empty=EmptyCmd(
                out=StringIO(), 
                err=StringIO(), 
                environ={},
                getuid=lambda: 123,
                list_volumes=lambda: ['/mnt'],
                fs = fs
                )
        empty.run('trash-empty')
        #assert_equals(['/mnt/.Trash/123/info/foo.trashinfo'], fs.removed_files())



# class TrashEmptyCommand_Test(TestCase):
# 
#     def test_it_deletes_all_files_in_trashcan(self):
#         self.given_a_trashcan_with(
#                 a_file(named="oldfile",trashed_on=days_ago(5)),
#                 a_file(named="newfile",trashed_on=today()))
# 
#         self.when_I_run('trash-empty')
# 
#         self.trashcan.should_not_contain_a_file_named("newfile")
#         self.trashcan.should_not_contain_a_file_named("oldfile")
# 
#     def test_it_deletes_only_file_older_than_X_days(self):
#         self.given_a_trashcan_with(
#                 a_file(named="oldfile",trashed_on=days_ago(5)),
#                 a_file(named="newfile",trashed_on=today()))
# 
#         self.when_I_run('trash-empty', '5')
# 
#         self.trashcan.should_contain_a_file_named("newfile")
#         self.trashcan.should_not_contain_a_file_named("oldfile")
# 
#     def given_a_trashcan_with(self, *trashed_files):
#         self.trashcan = FakeTrashCan(*trashed_files)
# 
#     def when_I_run(self, *command_line):
#         cmd=EmptyCmd(trashcan = self.trashcan, 
#                           now = today)
#         cmd.run(list(command_line))
# 
# 
# def today():
#     return to_date("2010-01-05")
# 
# def days_ago(days):
#     from datetime import timedelta
#     return today() - timedelta(days)
# 
# def to_date(string):
#     from datetime import datetime
#     return datetime.strptime(string, "%Y-%m-%d")
# 
# class a_file(object):
#     from datetime import datetime 
#     def __init__(self, named="", trashed_on=datetime(1970,1,1)):
#         self.name = named
#         self.deletion_date = trashed_on 
# 
#     def __repr__(self):
#         return "a_file(name='%s',deletion_date='%s')" % (self.name,self.deletion_date.strftime("%Y-%m-%d"))
# 
# class FakeTrashCan(object):
#     def __init__(self, *trashed_files):
#         self._trashed_files = list(trashed_files)
# 
#     def trashed_files(self):
#         for file in list(self._trashed_files):
#             yield file
# 
#     def purge(self, trashed_file):
#         self._trashed_files.remove(trashed_file) 
# 
#     def should_not_contain_a_file_named(self, name):
#         assert_false(self._contains_a_file_named(name), 
#                     ("Expected a file named '%s' *not* in %s ") % (name, self._trashed_files))
#         
#     def should_contain_a_file_named(self, name):
#         assert_true(self._contains_a_file_named(name), 
#                     ("Expected a file named '%s' in %s ") % (name, self._trashed_files))
# 
#     def _contains_a_file_named(self, name):
#         found = False
#         for trashed_file in self._trashed_files:
#             if trashed_file.name == name:
#                 found = True
#         return found
# 
