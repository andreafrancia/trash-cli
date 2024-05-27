import os

from six import binary_type

from tests.support.fs_fixture import FsFixture
from tests.support.trash_dirs.fake_trash_dir import \
    trashinfo_content_default_date
from trashcli.put.fs.real_fs import RealFs


class RestoreFileFixture:
    def __init__(self, XDG_DATA_HOME):
        self.XDG_DATA_HOME = XDG_DATA_HOME
        self.fx = FsFixture(RealFs())

    def having_a_trashed_file(self, path):
        self.fx.make_file('%s/info/foo.trashinfo' % self._trash_dir(),
                          trashinfo_content_default_date(path))
        self.fx.make_empty_file('%s/files/foo' % self._trash_dir())

    def make_file(self, filename,
                  contents=b'',  # type: binary_type
                  ):  # type: (...) -> None
        return self.fx.make_file(filename, contents)

    def make_empty_file(self, filename):
        return self.fx.make_empty_file(filename)

    def _trash_dir(self):
        return "%s/Trash" % self.XDG_DATA_HOME

    def file_should_have_been_restored(self, filename):
        assert os.path.exists(filename)
