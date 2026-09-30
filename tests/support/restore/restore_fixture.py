from tests.support.restore.fake_path_fs import FakePathFs


class RestoreFixture:
    def __init__(self,
                 fs,  # type: FakePathFs
                 ):
        self.fs = fs

    def make_trashed_file(self, from_path, trash_dir, time,
                          original_file_content):
        return self.fs.make_trashed_file(from_path, trash_dir, time,
                                         original_file_content)

    def add_trash_file(self, from_path, trash_dir, time,
                       original_file_content=''):
        return self.fs.add_trash_file(from_path, trash_dir, time,
                                      original_file_content)

    def add_trash_empty_file(self, from_path, trash_dir, time):
        return self.fs.add_trash_empty_file(from_path, trash_dir, time)

    def add_file(self, path, content=b''):
        return self.fs.add_file(path, content)
