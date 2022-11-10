from typing import Dict, List

from trashcli.fstab import Volumes
from trashcli.put.candidate import Candidate
from trashcli.put.gate import SameVolumeGate, HomeFallbackGate
from trashcli.put.path_maker import AbsolutePaths, RelativePaths
from trashcli.put.security_check import all_is_ok_rules, top_trash_dir_rules
from trashcli.trash import home_trash_dir, volume_trash_dir1, volume_trash_dir2


class TrashDirectoriesFinder:
    def __init__(self, volumes):  # type: (Volumes) -> None
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
                          check_type=all_is_ok_rules,
                          gate=gate))

        def add_top_trash_dir(path, volume):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=RelativePaths,
                          check_type=top_trash_dir_rules,
                          gate=SameVolumeGate))

        def add_alt_top_trash_dir(path, volume):
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=RelativePaths,
                          check_type=all_is_ok_rules,
                          gate=SameVolumeGate))

        if specific_trash_dir:
            path = specific_trash_dir
            volume = self.volumes.volume_of(path)
            trash_dirs.append(
                Candidate(trash_dir_path=path,
                          volume=volume,
                          path_maker_type=RelativePaths,
                          check_type=all_is_ok_rules,
                          gate=SameVolumeGate))
        else:
            for path, dir_volume in home_trash_dir(environ,
                                                   self.volumes.volume_of):
                add_home_trash(path, dir_volume, SameVolumeGate)
            for path, dir_volume in volume_trash_dir1(volume, uid):
                add_top_trash_dir(path, dir_volume)
            for path, dir_volume in volume_trash_dir2(volume, uid):
                add_alt_top_trash_dir(path, dir_volume)
            if home_fallback:
                for path, dir_volume in home_trash_dir(environ,
                                                       self.volumes.volume_of):
                    add_home_trash(path, dir_volume, HomeFallbackGate)
        return trash_dirs
