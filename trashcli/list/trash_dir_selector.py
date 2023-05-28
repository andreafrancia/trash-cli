# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
from typing import List, Dict, Iterator, Tuple

from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.dir_checker import DirChecker
from trashcli.lib.user_info import AllUsersInfoProvider, \
    SingleUserInfoProvider
from trashcli.trash_dirs_scanner import trash_dir_found, TrashDir, \
    TopTrashDirRules, TrashDirsScanner


class TrashDirsSelector:
    def __init__(self,
                 current_user_dirs,
                 all_users_dirs,
                 volumes  # type: VolumeOf
                 ):
        self.current_user_dirs = current_user_dirs
        self.all_users_dirs = all_users_dirs
        self.volumes = volumes

    def select(self,
               all_users_flag, # type: bool
               user_specified_dirs, # type: List[str]
               environ, # type: Dict[str, str]
               uid, # type: int
               ):  # type: (...) -> Iterator[Tuple[str, TrashDir]]
        if all_users_flag:
            for dir in self.all_users_dirs.scan_trash_dirs(environ, uid):
                yield dir
        else:
            if not user_specified_dirs:
                for dir in self.current_user_dirs.scan_trash_dirs(environ, uid):
                    yield dir
            for dir in user_specified_dirs:
                yield trash_dir_found, (
                    TrashDir(dir, self.volumes.volume_of(dir)))

    @staticmethod
    def make(volumes_listing,
             reader,  # type: TopTrashDirRules.Reader
             volumes  # type: VolumeOf
             ):
        user_info_provider = SingleUserInfoProvider()
        user_dir_scanner = TrashDirsScanner(user_info_provider,
                                            volumes_listing,
                                            TopTrashDirRules(reader),
                                            DirChecker())
        all_users_info_provider = AllUsersInfoProvider()
        all_users_scanner = TrashDirsScanner(all_users_info_provider,
                                             volumes_listing,
                                             TopTrashDirRules(reader),
                                             DirChecker())
        return TrashDirsSelector(user_dir_scanner,
                                 all_users_scanner,
                                 volumes)
