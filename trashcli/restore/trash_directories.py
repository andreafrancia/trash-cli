# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os

from trashcli.fs import list_files_in_dir
from trashcli.fstab import volume_of
from trashcli.lib.trash_dirs import (
    volume_trash_dir1, volume_trash_dir2, home_trash_dir)


class TrashDirectories2:
    def __init__(self, volume_of, trash_directories):
        self.volume_of = volume_of
        self.trash_directories = trash_directories

    def trash_directories_or_user(self, volumes, trash_dir_from_cli):
        if trash_dir_from_cli:
            return [(trash_dir_from_cli, self.volume_of(trash_dir_from_cli))]
        return self.trash_directories.all_trash_directories(volumes)


def make_trash_directories():
    trash_directories = TrashDirectories(volume_of, os.getuid(), os.environ)
    return TrashDirectories2(volume_of, trash_directories)


class TrashDirectories:
    def __init__(self, volume_of, uid, environ):
        self.volume_of = volume_of
        self.uid = uid
        self.environ = environ

    def all_trash_directories(self, volumes):
        for path1, volume1 in home_trash_dir(self.environ, self.volume_of):
            yield path1, volume1
        for volume in volumes:
            for path1, volume1 in volume_trash_dir1(volume, self.uid):
                yield path1, volume1
            for path1, volume1 in volume_trash_dir2(volume, self.uid):
                yield path1, volume1


class TrashDirectory:

    def all_info_files(self, path):
        norm_path = os.path.normpath(path)
        info_dir = os.path.join(norm_path, 'info')
        try:
            for info_file in list_files_in_dir(info_dir):
                if not os.path.basename(info_file).endswith('.trashinfo'):
                    yield ('non_trashinfo', info_file)
                else:
                    yield ('trashinfo', info_file)
        except OSError:  # when directory does not exist
            pass
