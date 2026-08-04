import os

from trashcli.fslib.real_fs_operations import RealHasStickyBit, RealMkDirs, \
    RealWriteFile, RealIsStickyDir


class RealFs1:
    def has_sticky_bit(self, path):
        return RealHasStickyBit().has_sticky_bit(path)

    def mkdirs(self, path):
        RealMkDirs().mkdirs(path)

    def make_file(self, filename, contents=''):
        self.make_parent_for(filename)
        self.write_file(filename, contents)

    def make_parent_for(self, path):
        parent = os.path.dirname(os.path.realpath(path))
        self.make_dirs(parent)

    def write_file(self, filename, contents):
        RealWriteFile().write_file(filename, contents)

    def make_dirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        assert os.path.isdir(path)

    def set_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode | stat.S_ISVTX)

    def make_empty_file(self, path):
        self.make_file(path, '')

    def unset_sticky_bit(self, path):
        import stat
        os.chmod(path, os.stat(path).st_mode & ~ stat.S_ISVTX)

    def is_sticky_dir(self, path):
        return RealIsStickyDir().is_sticky_dir(path)
