import os

from tests.support.fakes.fake_trash_dir import trashinfo_content_default_date
from tests.support.files import make_file


class RestoreFileFixture:
    def __init__(self, XDG_DATA_HOME):
        self.XDG_DATA_HOME = XDG_DATA_HOME

    def having_a_trashed_file(self, path):
        self.make_file('%s/info/foo.trashinfo' % self._trash_dir(),
                       trashinfo_content_default_date(path))
        self.make_file('%s/files/foo' % self._trash_dir())

    def make_file(self, filename, contents=''):
        return make_file(filename, contents)

    def make_empty_file(self, filename):
        return self.make_file(filename)

    def _trash_dir(self):
        return "%s/Trash" % self.XDG_DATA_HOME

    def file_should_have_been_restored(self, filename):
        assert os.path.exists(filename)
