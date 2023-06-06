import os
from typing import Iterable
from trashcli.compat import Protocol

from trashcli.fs import PathExists, IsStickyDir, IsSymLink
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.lib.dir_checker import DirChecker
from trashcli.lib.user_info import UserInfoProvider


class MyEnum(str):
    def __repr__(self):
        return str(self)


trash_dir_found = MyEnum('trash_dir_found')
trash_dir_skipped_because_parent_not_sticky = \
    MyEnum('trash_dir_skipped_because_parent_not_sticky')
trash_dir_skipped_because_parent_is_symlink = \
    MyEnum('trash_dir_skipped_because_parent_is_symlink')

top_trash_dir_does_not_exist = MyEnum('top_trash_dir_does_not_exist')
top_trash_dir_invalid_because_not_sticky = \
    MyEnum('top_trash_dir_invalid_because_not_sticky')
top_trash_dir_invalid_because_parent_is_symlink = \
    MyEnum('top_trash_dir_invalid_because_parent_is_symlink')
top_trash_dir_valid = MyEnum('top_trash_dir_valid')


class TrashDir(tuple):
    @property
    def path(self):
        return self[0]

    @property
    def volume(self):
        return self[1]

    def __new__(cls, path, volume):
        return tuple.__new__(TrashDir, (path, volume))

    def __repr__(self):
        return 'TrashDir(%r, %r)' % (self.path, self.volume)


class TopTrashDirRules:
    class Reader(PathExists, IsStickyDir, IsSymLink, Protocol):
        pass

    def __init__(self, reader):  # type: (Reader) -> None
        self.reader = reader

    def valid_to_be_read(self, path):
        parent_trashdir = os.path.dirname(path)
        if not self.reader.exists(path):
            return top_trash_dir_does_not_exist
        if not self.reader.is_sticky_dir(parent_trashdir):
            return top_trash_dir_invalid_because_not_sticky
        if self.reader.is_symlink(parent_trashdir):
            return top_trash_dir_invalid_because_parent_is_symlink
        else:
            return top_trash_dir_valid


class TrashDirsScanner:
    def __init__(self,
                 user_info_provider,  # type: UserInfoProvider
                 volumes_listing,  # type: VolumesListing
                 top_trash_dir_rules,  # type: TopTrashDirRules
                 dir_checker,  # type: DirChecker
                 ):
        self.user_info_provider = user_info_provider
        self.volumes_listing = volumes_listing  # type: VolumesListing
        self.top_trash_dir_rules = top_trash_dir_rules
        self.dir_checker = dir_checker

    def scan_trash_dirs(self, environ, uid):
        for user_info in self.user_info_provider.get_user_info(environ, uid):
            for path in user_info.home_trash_dir_paths:
                yield trash_dir_found, TrashDir(path, '/')
            for volume in self.volumes_listing.list_volumes(environ):
                top_trash_dir_path = os.path.join(volume, '.Trash',
                                                  str(user_info.uid))
                result = self.top_trash_dir_rules.valid_to_be_read(
                    top_trash_dir_path)
                if result == top_trash_dir_valid:
                    yield trash_dir_found, TrashDir(top_trash_dir_path, volume)
                elif result == top_trash_dir_invalid_because_not_sticky:
                    yield trash_dir_skipped_because_parent_not_sticky, (
                        top_trash_dir_path,)
                elif result == top_trash_dir_invalid_because_parent_is_symlink:
                    yield trash_dir_skipped_because_parent_is_symlink, (
                        top_trash_dir_path,)
                alt_top_trash_dir = os.path.join(volume,
                                                 '.Trash-%s' % user_info.uid)
                if self.dir_checker.is_dir(alt_top_trash_dir):
                    yield trash_dir_found, TrashDir(alt_top_trash_dir, volume)


def only_found(events, # type: Iterable[TrashDir]
               ):  # type: (...) -> Iterable[TrashDir]
    for event, args in events:
        if event == trash_dir_found:
            yield args
