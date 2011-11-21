from nose.tools import assert_true, assert_false
from unittest import TestCase
from trashcli.trash import EmptyCmd

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
