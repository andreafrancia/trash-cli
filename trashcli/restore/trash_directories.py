# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from abc import abstractmethod, ABCMeta
from typing import Dict

import six

from trashcli.fstab.volumes import Volumes
from trashcli.lib.trash_dirs import (
    volume_trash_dir1, volume_trash_dir2, home_trash_dir)
from trashcli.list_mount_points import MountPointsListing


@six.add_metaclass(ABCMeta)
class TrashDirectories:
    @abstractmethod
    def list_trash_dirs(self, trash_dir_from_cli):
        raise NotImplementedError()


class TrashDirectoriesImpl(TrashDirectories):
    def __init__(self,
                 mount_point_listing,  # type: MountPointsListing
                 volumes,  # type: Volumes
                 uid,  # type: int
                 environ,
                 ):
        trash_directories1 = TrashDirectories1(mount_point_listing,
                                               volumes, uid, environ)
        self.trash_directories2 = TrashDirectories2(volumes,
                                                    trash_directories1)

    def list_trash_dirs(self, trash_dir_from_cli):
        return self.trash_directories2.trash_directories_or_user(
            trash_dir_from_cli)


class TrashDirectories2:
    def __init__(self,
                 volumes,  # type: Volumes
                 trash_directories,  # type: TrashDirectories1
                 ):
        self.volumes = volumes
        self.trash_directories = trash_directories

    def trash_directories_or_user(self, trash_dir_from_cli):
        if trash_dir_from_cli:
            return [(trash_dir_from_cli,
                     self.volumes.volume_of(trash_dir_from_cli))]
        return self.trash_directories.all_trash_directories()


class TrashDirectories1:
    def __init__(self,
                 mount_point_listing,  # type: MountPointsListing
                 volumes,  # type: Volumes
                 uid,  # type: int
                 environ,  # type: Dict[str, str]
                 ):
        self.mount_point_listing = mount_point_listing
        self.volumes = volumes
        self.uid = uid
        self.environ = environ

    def all_trash_directories(self):
        volumes_to_check = self.mount_point_listing.list_mount_points()
        for path1, volume1 in home_trash_dir(self.environ, self.volumes):
            yield path1, volume1
        for volume in volumes_to_check:
            for path1, volume1 in volume_trash_dir1(volume, self.uid):
                yield path1, volume1
            for path1, volume1 in volume_trash_dir2(volume, self.uid):
                yield path1, volume1
