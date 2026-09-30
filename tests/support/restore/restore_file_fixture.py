import os

from tests.support.fakes.fake_trash_dir import trashinfo_content_default_date
from trashcli.put.fs.fs import Fs


class RestoreFileFixture:
    def __init__(self,
                 XDG_DATA_HOME,
                 fs,  # type: Fs
                 ):
        self.XDG_DATA_HOME = XDG_DATA_HOME
        self.fs = fs

    def having_a_trashed_file(self, path):
        self.make_file('%s/info/foo.trashinfo' % self._trash_dir(),
                       trashinfo_content_default_date(path))
        self.make_file('%s/files/foo' % self._trash_dir())

    def make_file(self, filename, contents=''):
        parent = os.path.dirname(self.fs.realpath(filename))
        if not self.fs.exists(parent):
            self.fs.makedirs(parent, 0o755)
        self.fs.make_file(filename, contents)

    def make_empty_file(self, filename):
        return self.make_file(filename)

    def _trash_dir(self):
        return "%s/Trash" % self.XDG_DATA_HOME

    def file_should_have_been_restored(self, filename):
        assert self.fs.exists(filename)
