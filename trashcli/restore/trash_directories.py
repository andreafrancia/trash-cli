# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from abc import abstractmethod, ABCMeta

import os
import six
from typing import Optional

from trashcli.fstab.mount_points_listing import MountPointListFs
from trashcli.fstab.volume_of import VolumeOf
from trashcli.fstab.volumes import Volumes
from trashcli.lib.environ import Environ
from trashcli.lib.trash_dirs import (
    volume_trash_dir1, volume_trash_dir2, home_trash_dir)
from trashcli.restore.restore_logger import RestoreLogger
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
                 logger,  # type: RestoreLogger
                 ):
        trash_directories1 = TrashDirectories1(volumes, uid, environ,
                                               top_trash_dir_rules, logger)
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
                 logger,  # type: RestoreLogger
                 ):
        self.volumes = volumes
        self.uid = uid
        self.environ = environ
        self.top_trash_dir_rules = top_trash_dir_rules
        self.logger = logger

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
        reason = self._distrust_reason(trash_dir)
        if reason is not None:
            self.logger.warning(
                "TrashDir skipped because %s: %s" % (reason, trash_dir))
            return False
        return True

    def _distrust_reason(self, trash_dir):
        reader = self.top_trash_dir_rules.reader
        for sub_dir in ('info', 'files'):
            path = os.path.join(trash_dir, sub_dir)
            if reader.is_symlink(path):
                return "its %s dir is a symbolic link" % sub_dir
            if reader.is_world_writable(path):
                return "its %s dir is world writable" % sub_dir
        return None
