class Dirs:
    def list_files_in_dir(self, path):
        import os
        if not os.path.isdir(path):
            return []
        return os.listdir(path)

    def list_files_in_subdir(self, path, subdir):
        return ["%s/%s" % (subdir, f) for f in
                self.list_files_in_dir(path / subdir)]

    def remove_dir_if_exists(self, dir):
        import os
        if os.path.exists(dir):
            os.rmdir(dir)

list_files_in_dir = Dirs().list_files_in_dir
list_files_in_subdir = Dirs().list_files_in_subdir
remove_dir_if_exists = Dirs().remove_dir_if_exists