import os

from six import text_type

from trashcli.lib import TrashInfoContent
from trashcli.put.fs.fs import Fs


class FsFixture:
    def __init__(self,
                 fs,  # type: Fs
                 ):
        self.fs = fs

    def require_empty_dir(self, path):
        self.fs.mkdir_p(path)
        self.check_empty_dir(path)

    def make_readable(self, path):
        self.fs.chmod(path, 0o700)

    def make_empty_dir(self, path):
        self.fs.mkdir(path)
        self.check_empty_dir(path)

    def check_empty_dir(self, path):
        assert self.fs.isdir(path)
        assert [] == list(self.fs.listdir(path))

    def make_text_file_p(self,
                         path,
                         contents='',  # type: text_type
                         ):  # type: (...) -> None
        self.make_parent_for(path)
        self.fs.write_file(path, contents.encode('utf-8'))

    def make_empty_file(self, path):
        self.make_file(path, b'')

    def make_unreadable_file(self, path,
                             ):  # type: (...) -> None
        self.fs.make_file_p(path, b'')
        self.fs.chmod(path, 0)


    def make_parent_for(self, path):
        parent = os.path.dirname(self.fs.realpath(path))
        self.fs.mkdir_p(parent)


    def make_file(self, path,
                  contents,  # type: TrashInfoContent
                  ):  # type: (...) -> None
        self.fs.make_file_p(path, contents)

    def listdir(self, path):
        return self.fs.listdir(path)

    def make_sticky_dir(self, path):
        self.fs.mkdir(path)
        self.fs.set_sticky_bit(path)

    def make_unsticky_dir(self, path):
        self.fs.mkdir(path)
        self.fs.unset_sticky_bit(path)

    def assert_is_dir(self, path):
        assert self.fs.isdir(path)

    def make_a_symlink_to_a_dir(self, path):
        dest = "%s-dest" % path
        self.fs.mkdir(dest)
        rel_dest = os.path.basename(dest)
        self.fs.symlink(rel_dest, path)

    def make_dir(self, path):
        self.fs.mkdir(path)

    def exists(self, path):
        return self.fs.exists(path)

    def make_unreadable_dir(self, path):
        self.fs.mkdir_p(path)
        self.fs.chmod(path, 0o300)
