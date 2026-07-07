# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from abc import abstractmethod, ABCMeta

import os
import stat
import six
from typing import Optional

from trashcli.fstab.volume_of import VolumeOf
from trashcli.fstab.volumes import Volumes
from trashcli.lib.environ import Environ
from trashcli.lib.trash_dirs import (
    volume_trash_dir1, volume_trash_dir2, home_trash_dir)
from trashcli.trash_dirs_scanner import top_trash_dir_valid


@six.add_metaclass(ABCMeta)
class TrashDirectories:
    @abstractmethod
    def list_trash_dirs(self, trash_dir_from_cli):
        raise NotImplementedError()


class TrashDirectoriesImpl(TrashDirectories):
    def __init__(self,
                 volumes,  # type: Volumes
                 uid,  # type: int
                 environ,
                 top_trash_dir_rules,
                 ):
        trash_directories1 = TrashDirectories1(volumes, uid, environ,
                                               top_trash_dir_rules)
        self.trash_directories2 = TrashDirectories2(volumes,
                                                    trash_directories1)

    def list_trash_dirs(self,
                        trash_dir_from_cli,  # type: Optional[str]
                        ):
        return self.trash_directories2.trash_directories_or_user(
            trash_dir_from_cli)


class TrashDirectories2:
    def __init__(self,
                 volume_of,  # type: VolumeOf
                 trash_directories,  # type: TrashDirectories1
                 ):
        self.volume_of = volume_of
        self.trash_directories = trash_directories

    def trash_directories_or_user(self,
                                  trash_dir_from_cli,  # type: Optional[str]
                                  ):
        if trash_dir_from_cli:
            return [(trash_dir_from_cli,
                     self.volume_of.volume_of(trash_dir_from_cli))]
        return self.trash_directories.all_trash_directories()



class TrashDirectories1:
    def __init__(self,
                 volumes,  # type: Volumes
                 uid,  # type: int
                 environ,  # type: Environ
                 top_trash_dir_rules,
                 ):
        self.volumes = volumes
        self.uid = uid
        self.environ = environ
        self.top_trash_dir_rules = top_trash_dir_rules

    def all_trash_directories(self):
        volumes_to_check = self.volumes.list_mount_points()
        for path1, volume1 in home_trash_dir(self.environ, self.volumes):
            if self._is_trusted(path1):
                yield path1, volume1
        for volume in volumes_to_check:
            for path1, volume1 in volume_trash_dir1(volume, self.uid):
                # Read a shared .Trash/$uid only when its parent is sticky and not a symlink.
                if self.top_trash_dir_rules.valid_to_be_read(
                        path1) == top_trash_dir_valid and self._is_trusted(path1):
                    yield path1, volume1
            for path1, volume1 in volume_trash_dir2(volume, self.uid):
                if self._is_trusted(path1):
                    yield path1, volume1

    def _is_trusted(self, trash_dir):
        # Distrust a trash dir if others could plant or redirect its entries.
        info = os.path.join(trash_dir, 'info')
        files = os.path.join(trash_dir, 'files')
        reader = self.top_trash_dir_rules.reader
        if reader.is_symlink(info) or reader.is_symlink(files):
            return False
        return not self._world_writable(info)

    @staticmethod
    def _world_writable(path):
        try:
            return bool(os.stat(path).st_mode & stat.S_IWOTH)
        except OSError:
            return False
