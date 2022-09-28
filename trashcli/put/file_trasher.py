import os
import random
from datetime import datetime
from typing import Callable, Dict

from trashcli.fstab import Volumes
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import MyLogger
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.rules import AllIsOkRules, TopTrashDirRules
from trashcli.put.suffix import Suffix
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.real_fs import RealFs
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trash_result import TrashResult
from trashcli.put.values import absolute_paths, relative_paths, \
    all_is_ok_rules, top_trash_dir_rules


class PossibleTrashDirectories:
    def __init__(self, trash_directories_finder, user_trash_dir,
                 environ, uid):
        self.trash_directories_finder = trash_directories_finder
        self.user_trash_dir = user_trash_dir
        self.environ = environ
        self.uid = uid

    def trash_directories_for(self, volume_of_file_to_be_trashed):
        return self.trash_directories_finder. \
            possible_trash_directories_for(volume_of_file_to_be_trashed,
                                           self.user_trash_dir, self.environ,
                                           self.uid)

class FileTrasher:

    def __init__(self, fs, volumes, realpath, now, trash_directories_finder,
                 parent_path):  # type: (RealFs, Volumes, Callable[[str], str], Callable[[], datetime], TrashDirectoriesFinder, Callable[[str], str]) -> None
        self.fs = fs
        self.volumes = volumes
        self.realpath = realpath
        self.now = now
        self.trash_directories_finder = trash_directories_finder
        self.parent_path = parent_path

    def trash_file(self,
                   file,  # type: str
                   forced_volume,
                   user_trash_dir,
                   result,  # type: TrashResult
                   logger,  # type: MyLogger
                   reporter,  # type: TrashPutReporter
                   environ,  # type: Dict[str, str]
                   uid,  # type: int
                   possible_trash_directories = None,
                   ):
        volume_of_file_to_be_trashed = forced_volume or \
                                       self.volume_of_parent(file)

        possible_trash_directories = possible_trash_directories or PossibleTrashDirectories(
            self.trash_directories_finder,
            user_trash_dir,
            environ, uid)
        candidates = possible_trash_directories.trash_directories_for(
            volume_of_file_to_be_trashed)
        reporter.volume_of_file(volume_of_file_to_be_trashed)
        file_has_been_trashed = False
        for path, volume, path_maker, checker in candidates:
            suffix = Suffix(random.randint)
            info_dir_path = os.path.join(path, 'info')
            info_dir = InfoDir(info_dir_path, self.fs, logger, suffix)
            path_maker = {absolute_paths: AbsolutePaths(),
                          relative_paths: TopDirRelativePaths(volume)}[
                path_maker]
            checker = {top_trash_dir_rules: TopTrashDirRules(),
                       all_is_ok_rules: AllIsOkRules()}[checker]
            trash_dir = TrashDirectoryForPut(path,
                                             volume,
                                             self.fs,
                                             path_maker,
                                             info_dir)
            trash_dir_is_secure, messages = checker.check_trash_dir_is_secure(
                trash_dir.path,
                self.fs)
            for message in messages:
                reporter.log_info(message)

            if trash_dir_is_secure:
                volume_of_trash_dir = self.volumes.volume_of(
                    self.realpath(trash_dir.path))
                reporter.trash_dir_with_volume(trash_dir.path,
                                               volume_of_trash_dir)
                if self._file_could_be_trashed_in(volume_of_file_to_be_trashed,
                                                  volume_of_trash_dir):
                    try:
                        self.fs.ensure_dir(path, 0o700)
                        self.fs.ensure_dir(os.path.join(path, 'files'), 0o700)
                        trash_dir.trash2(file, self.now)
                        reporter.file_has_been_trashed_in_as(
                            file,
                            trash_dir.path)
                        file_has_been_trashed = True

                    except (IOError, OSError) as error:
                        reporter.unable_to_trash_file_in_because(
                            file, trash_dir.path, error)
            else:
                reporter.trash_dir_is_not_secure(trash_dir.path)

            if file_has_been_trashed: break

        if not file_has_been_trashed:
            result = result.mark_unable_to_trash_file()
            reporter.unable_to_trash_file(file)

        return result

    def _file_could_be_trashed_in(self,
                                  volume_of_file_to_be_trashed,
                                  volume_of_trash_dir):
        return volume_of_trash_dir == volume_of_file_to_be_trashed

    def volume_of_parent(self, file):
        return self.volumes.volume_of(self.parent_path(file))


class TopDirRelativePaths:
    def __init__(self, topdir):
        self.topdir = topdir

    def calc_parent_path(self, parent):
        if (parent == self.topdir) or parent.startswith(
                self.topdir + os.path.sep):
            parent = parent[len(self.topdir + os.path.sep):]
        return parent


class AbsolutePaths:

    @staticmethod
    def calc_parent_path(parent):
        return parent
