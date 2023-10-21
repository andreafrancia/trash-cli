# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from abc import abstractmethod, ABCMeta

import six
from typing import Optional

from trashcli.fstab.volume_of import VolumeOf
from trashcli.fstab.volumes import Volumes
from trashcli.lib.environ import Environ
from trashcli.lib.trash_dirs import (
    volume_trash_dir1, volume_trash_dir2, home_trash_dir)


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
                 ):
        trash_directories1 = TrashDirectories1(volumes, uid, environ)
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
                 ):
        self.volumes = volumes
        self.uid = uid
        self.environ = environ

    def all_trash_directories(self):
        volumes_to_check = self.volumes.list_mount_points()
        for path1, volume1 in home_trash_dir(self.environ, self.volumes):
            yield path1, volume1
        for volume in volumes_to_check:
            for path1, volume1 in volume_trash_dir1(volume, self.uid):
                yield path1, volume1
            for path1, volume1 in volume_trash_dir2(volume, self.uid):
                yield path1, volume1
