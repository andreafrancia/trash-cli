from typing import Dict, List, Tuple

from trashcli.fstab import Volumes
from trashcli.put.values import absolute_paths, relative_paths, \
    all_is_ok_rules, top_trash_dir_rules
from trashcli.trash import home_trash_dir, volume_trash_dir1, volume_trash_dir2


class TrashDirectoriesFinder:
    def __init__(self, uid, volumes):  # type: (int, Volumes) -> None
        self.uid = uid
        self.volumes = volumes

    def possible_trash_directories_for(self,
                                       volume,
                                       specific_trash_dir,
                                       environ):  # type: (str, str, Dict[str, str]) -> List[Tuple[str, str, str, str]]
        trash_dirs = []

        def add_home_trash(path, volume):
            trash_dirs.append((path, volume, absolute_paths, all_is_ok_rules))

        def add_top_trash_dir(path, volume):
            trash_dirs.append(
                (path, volume, relative_paths, top_trash_dir_rules))

        def add_alt_top_trash_dir(path, volume):
            trash_dirs.append((path, volume, relative_paths, all_is_ok_rules))

        if specific_trash_dir:
            path = specific_trash_dir
            volume = self.volumes.volume_of(path)
            trash_dirs.append((path, volume, relative_paths, all_is_ok_rules))
        else:
            for path, dir_volume in home_trash_dir(environ,
                                                   self.volumes.volume_of):
                add_home_trash(path, dir_volume)
            for path, dir_volume in volume_trash_dir1(volume, self.uid):
                add_top_trash_dir(path, dir_volume)
            for path, dir_volume in volume_trash_dir2(volume, self.uid):
                add_alt_top_trash_dir(path, dir_volume)
        return trash_dirs
