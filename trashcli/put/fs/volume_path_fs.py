import os


class VolumePathFs:
    def is_root_volume(self, volume_path):  # type: (str) -> bool
        return volume_path == os.path.sep

    def is_outside_of(self, path, volume_path):  # type: (str, str) -> bool
        rel = os.path.relpath(path, os.path.normpath(volume_path))
        return rel == os.pardir or rel.startswith(os.pardir + os.sep)
