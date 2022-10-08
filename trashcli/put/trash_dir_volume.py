import os


class TrashDirVolume:
    def __init__(self, volumes, realpath):
        self.volumes = volumes
        self.realpath = realpath

    def volume_of_trash_dir(self, trash_dir_volume):
        norm_trash_dir_path = os.path.normpath(trash_dir_volume)
        return self.volumes.volume_of(
            self.realpath(norm_trash_dir_path))
