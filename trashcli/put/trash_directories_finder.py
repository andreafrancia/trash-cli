from typing import Dict, List, Tuple

from trashcli.fstab import Volumes
from trashcli.put.path_maker import PathMakerType
from trashcli.put.security_check import all_is_ok_rules, top_trash_dir_rules
from trashcli.trash import home_trash_dir, volume_trash_dir1, volume_trash_dir2


class TrashDirectoriesFinder:
    def __init__(self, volumes):  # type: (Volumes) -> None
        self.volumes = volumes

    def possible_trash_directories_for(self, volume, specific_trash_dir,
                                       environ,
                                       uid):  # type: (str, str, Dict[str, str], int) -> List[Tuple[str, str, str, str]]
        trash_dirs = []

        def add_home_trash(path, volume):
            trash_dirs.append((path, volume, PathMakerType.absolute_paths, all_is_ok_rules))

        def add_top_trash_dir(path, volume):
            trash_dirs.append(
                (path, volume, PathMakerType.relative_paths, top_trash_dir_rules))

        def add_alt_top_trash_dir(path, volume):
            trash_dirs.append((path, volume, PathMakerType.relative_paths, all_is_ok_rules))

        if specific_trash_dir:
            path = specific_trash_dir
            volume = self.volumes.volume_of(path)
            trash_dirs.append((path, volume, PathMakerType.relative_paths, all_is_ok_rules))
        else:
            for path, dir_volume in home_trash_dir(environ,
                                                   self.volumes.volume_of):
                add_home_trash(path, dir_volume)
            for path, dir_volume in volume_trash_dir1(volume, uid):
                add_top_trash_dir(path, dir_volume)
            for path, dir_volume in volume_trash_dir2(volume, uid):
                add_alt_top_trash_dir(path, dir_volume)
        return trash_dirs
