import os


class TrashDirVolume:
    def __init__(self, volumes, fs):
        self.volumes = volumes
        self.fs = fs

    def volume_of_trash_dir(self, trash_dir_volume):
        norm_trash_dir_path = os.path.normpath(trash_dir_volume)
        return self.volumes.volume_of(
            self.fs.realpath(norm_trash_dir_path))
