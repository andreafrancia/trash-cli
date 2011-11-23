from nose.tools import assert_equals
from trashcli.trash2 import read_deletion_date

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
