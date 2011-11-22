from nose.tools import assert_equals, assert_not_equals

class EmptyCmd():
    def __init__(self, out, err, environ):
        self.out = out
        self.err = err
        self.environ = environ
    def run(self, *argv):
        for info_dir in self._info_dirs():
            infodir=InfoDir(info_dir)
            for entry in infodir.trashinfo_entries():
                infodir.remove_file_if_exists(entry)
                infodir.remove_trashinfo(entry)
            for entry in infodir.files():
                infodir.remove_existring_file(entry)
    def _info_dirs(self):
        if 'XDG_DATA_HOME' in self.environ:
            yield '%s/Trash/info' % self.environ['XDG_DATA_HOME']
        elif 'HOME' in self.environ:
            yield '%s/.local/share/Trash/info' % self.environ['HOME']

class InfoDir:
    def __init__(self, path):
        self.path = path
    def files_dir(self):
        files_dir = os.path.join(os.path.dirname(self.path), 'files')
        return files_dir
    def trashinfo_entries(self):
        for entry in self._entries_if_dir_exists(self.path):
            if entry.endswith('.trashinfo'):
                yield entry
    def remove_trashinfo(self, entry):
        os.remove(os.path.join(self.path, entry))
    def remove_file_if_exists(self, trashinfo_entry):
        entry=trashinfo_entry[:-len('.trashinfo')]
        path = os.path.join(self.files_dir(), entry)
        if os.path.exists(path): os.remove(path)
    def remove_existring_file(self, entry):
        os.remove(os.path.join(self.files_dir(), entry))
    def files(self):
        return self._entries_if_dir_exists(self.files_dir())
    def _entries_if_dir_exists(self, path):
        return entries_if_dir_exists(path)

def entries_if_dir_exists(path):
    if os.path.exists(path):
        for entry in os.listdir(path):
            yield entry

from StringIO import StringIO
import os

class TestEmptyCmd():
    def setUp(self):
        require_empty_dir('.local')
        self.out=StringIO()
        self.err=StringIO()
        self.environ = { 'XDG_DATA_HOME': '.local' }
    def run(self):
        EmptyCmd(
            out = self.out, 
            err = self.err, 
            environ = self.environ).run()

    def test_it_removes_an_info_file(self):
        touch(                    '.local/Trash/info/foo.trashinfo')
        self.run()
        assert not os.path.exists('.local/Trash/info/foo.trashinfo')

    def test_it_removes_multiple_info_files(self):
        touch('.local/Trash/info/foo.trashinfo')
        touch('.local/Trash/info/bar.trashinfo')
        touch('.local/Trash/info/baz.trashinfo')
        assert_not_equals([],list(os.listdir('.local/Trash/info/')))

        self.run()

        assert_equals([],list(os.listdir('.local/Trash/info/')))

    def test_it_removes_files(self):
        touch('.local/Trash/info/foo.trashinfo')
        touch('.local/Trash/files/foo')
        assert_not_equals([],list(os.listdir('.local/Trash/files/')))

        self.run()

        assert_equals([],list(os.listdir('.local/Trash/files/')))
    
    def test_it_keep_unknown_files_in_infodir(self):
        touch('.local/Trash/info/not-a-trashinfo')

        self.run()

        assert os.path.exists('.local/Trash/info/not-a-trashinfo')

    def test_it_removes_orphan_files(self):
        touch(                    '.local/Trash/files/a-file-without-any-associated-trashinfo')
        assert os.path.exists(    '.local/Trash/files/a-file-without-any-associated-trashinfo')

        self.run()

        assert not os.path.exists('.local/Trash/files/a-file-without-any-associated-trashinfo')


def touch(filename):
    import os
    parent = os.path.dirname(filename)
    if not os.path.isdir(parent): os.makedirs(parent)
    file(filename, 'w').write('')
    assert os.path.isfile(filename)

def require_empty_dir(dirname):
    import os
    import shutil
    if os.path.exists(dirname): shutil.rmtree(dirname)
    os.makedirs(dirname)
    assert os.path.isdir(dirname)

    


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
