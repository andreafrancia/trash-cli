# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import List

from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.environ import Environ
from trashcli.lib.trash_dirs import (
    volume_trash_dir1, volume_trash_dir2, home_trash_dir)
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.check_type import NoCheck, TopTrashDirCheck
from trashcli.put.core.path_maker_type import PathMakerType
from trashcli.put.gate import Gate


class TrashDirectoriesFinder:
    def __init__(self,
                 volumes,  # type: VolumeOf
                 ):
        self.volumes = volumes

    def possible_trash_directories_for(self,
                                       volume,  # type: str
                                       specific_trash_dir,  # type: str
                                       environ,  # type: Environ
                                       uid,  # type: int
                                       home_fallback,  # type: bool
                                       ):  # type: (...) -> List[Candidate]
        trash_dirs = []

        def add_home_trash(path, volume, gate):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=PathMakerType.AbsolutePaths,
                          check_type=NoCheck,
                          gate=gate))

        def add_top_trash_dir(path, volume):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=PathMakerType.RelativePaths,
                          check_type=TopTrashDirCheck,
                          gate=Gate.SameVolume))

        def add_alt_top_trash_dir(path, volume):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=PathMakerType.RelativePaths,
                          check_type=NoCheck,
                          gate=Gate.SameVolume))

        if specific_trash_dir:
            path = specific_trash_dir
            volume = self.volumes.volume_of(path)
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=PathMakerType.RelativePaths,
                          check_type=NoCheck,
                          gate=Gate.SameVolume))
        else:
            for path, dir_volume in home_trash_dir(environ,
                                                   self.volumes):
                add_home_trash(path, dir_volume, Gate.SameVolume)
            for path, dir_volume in volume_trash_dir1(volume, uid):
                add_top_trash_dir(path, dir_volume)
            for path, dir_volume in volume_trash_dir2(volume, uid):
                add_alt_top_trash_dir(path, dir_volume)
            if home_fallback:
                for path, dir_volume in home_trash_dir(environ,
                                                       self.volumes):
                    add_home_trash(path, dir_volume, Gate.HomeFallback)
        return trash_dirs
