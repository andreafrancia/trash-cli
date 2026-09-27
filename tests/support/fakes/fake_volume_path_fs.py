import posixpath

from trashcli.put.fs.volume_path_fs import VolumePathFs


class FakeVolumePathFs(VolumePathFs):
    # fake filesystems only know about posix-like paths, so volume checks are purely lexical
    def is_root_volume(self, volume_path):  # type: (str) -> bool
        return volume_path == '/'

    def is_outside_of(self, path, volume_path):  # type: (str, str) -> bool
        rel = posixpath.relpath(path, posixpath.normpath(volume_path))
        return rel == '..' or rel.startswith('../')
