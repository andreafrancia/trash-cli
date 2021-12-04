import os
import shutil
import tempfile


def list_trash_dir(trash_dir_path):
    return (list_files_in_subdir(trash_dir_path, 'info') +
            list_files_in_subdir(trash_dir_path, 'files'))


def list_files_in_subdir(path, subdir):
    return ["%s/%s" % (subdir, f) for f in list_files_in_dir(path / subdir)]


def list_files_in_dir(path):
    if not os.path.isdir(path):
        return []
    return os.listdir(path)


class MyPath(str):

    def __truediv__(self, other_path):
        return self.path_join(other_path)

    def __div__(self, other_path):
        return self.path_join(other_path)

    def path_join(self, other_path):
        return MyPath(os.path.join(self, other_path))

    def clean_up(self):
        shutil.rmtree(self)

    @classmethod
    def make_temp_dir(cls):
        return cls(os.path.realpath(tempfile.mkdtemp(suffix="_trash_cli_test")))
