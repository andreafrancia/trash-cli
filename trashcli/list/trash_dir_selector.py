from trashcli.fstab import Volumes
from trashcli.trash import UserInfoProvider, DirChecker, AllUsersInfoProvider
from trashcli.trash_dirs_scanner import trash_dir_found, TrashDir, \
    TopTrashDirRules, TrashDirsScanner


class TrashDirsSelector:
    def __init__(self,
                 current_user_dirs,
                 all_users_dirs,
                 volumes  # type: Volumes
                 ):
        self.current_user_dirs = current_user_dirs
        self.all_users_dirs = all_users_dirs
        self.volumes = volumes

    def select(self,
               all_users_flag,
               user_specified_dirs,
               environ,
               uid): # type (bool, List[str], Dict[str, str], int) -> Iterator[Tuple[str, TrashDir[str, str]]]
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
             volumes  # type: Volumes
             ):
        user_info_provider = UserInfoProvider()
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
