import os
import shutil
import tempfile


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
        return cls(os.path.realpath(tempfile.mkdtemp()))
