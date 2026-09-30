# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
class FakeFileSystem:
    def __init__(self):
        self.files = {}
        self.dirs = {}

    def read_file(self, path):
        return self.files[path]

    def exists(self, path):
        return path in self.files

    def entries_if_dir_exists(self, path):
        return self.dirs.get(path, [])

    def create_fake_file(self, path, contents=''):
        import os
        self.files[path] = contents
        self.create_fake_dir(os.path.dirname(path), os.path.basename(path))

    def create_fake_dir(self, dir_path, *dir_entries):
        self.dirs[dir_path] = dir_entries
