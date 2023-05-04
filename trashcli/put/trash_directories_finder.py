# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import Dict, List

from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.trash_dirs import (
    volume_trash_dir1, volume_trash_dir2, home_trash_dir)
from trashcli.put.candidate import Candidate
from trashcli.put.gate import SameVolumeGate, HomeFallbackGate
from trashcli.put.path_maker import AbsolutePaths, RelativePaths
from trashcli.put.security_check import NoCheck, TopTrashDirCheck


class TrashDirectoriesFinder:
    def __init__(self,
                 volumes,  # type: VolumeOf
                 ):
        self.volumes = volumes

    def possible_trash_directories_for(self,
                                       volume,  # type: str
                                       specific_trash_dir,  # type: str
                                       environ,  # type: Dict[str, str]
                                       uid,  # type: int
                                       home_fallback,  # type: bool
                                       ):  # type: (...) -> List[Candidate]
        trash_dirs = []

        def add_home_trash(path, volume, gate):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=AbsolutePaths,
                          check_type=NoCheck,
                          gate=gate))

        def add_top_trash_dir(path, volume):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=RelativePaths,
                          check_type=TopTrashDirCheck,
                          gate=SameVolumeGate))

        def add_alt_top_trash_dir(path, volume):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=RelativePaths,
                          check_type=NoCheck,
                          gate=SameVolumeGate))

        if specific_trash_dir:
            path = specific_trash_dir
            volume = self.volumes.volume_of(path)
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=RelativePaths,
                          check_type=NoCheck,
                          gate=SameVolumeGate))
        else:
            for path, dir_volume in home_trash_dir(environ,
                                                   self.volumes):
                add_home_trash(path, dir_volume, SameVolumeGate)
            for path, dir_volume in volume_trash_dir1(volume, uid):
                add_top_trash_dir(path, dir_volume)
            for path, dir_volume in volume_trash_dir2(volume, uid):
                add_alt_top_trash_dir(path, dir_volume)
            if home_fallback:
                for path, dir_volume in home_trash_dir(environ,
                                                       self.volumes):
                    add_home_trash(path, dir_volume, HomeFallbackGate)
        return trash_dirs
