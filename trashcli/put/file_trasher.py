import errno
import os
import random
from datetime import datetime
from typing import Callable, Dict

from trashcli.fstab import Volumes
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.real_fs import RealFs
from trashcli.put.values import absolute_paths, relative_paths, \
    all_is_ok_rules, top_trash_dir_rules
from trashcli.py2compat import url_quote
from trashcli.trash import path_of_backup_copy


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
                   ):
        volume_of_file_to_be_trashed = forced_volume or \
                                       self.volume_of_parent(file)
        candidates = self.trash_directories_finder. \
            possible_trash_directories_for(volume_of_file_to_be_trashed,
                                           user_trash_dir, environ)
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


def parent_realpath(path):
    parent = os.path.dirname(path)
    return os.path.realpath(parent)


class TrashDirectoryForPut:
    def __init__(self, path, volume, fs, path_maker, info_dir):
        self.path = os.path.normpath(path)
        self.volume = volume
        self.fs = fs
        self.path_maker = path_maker
        self.info_dir = info_dir

    def trash2(self, path, now):
        path = os.path.normpath(path)

        original_location = self.path_for_trash_info_for_file(path)

        basename = os.path.basename(original_location)
        content = format_trashinfo(original_location, now())
        trash_info_file = self.info_dir.persist_trash_info(basename, content)

        where_to_store_trashed_file = path_of_backup_copy(trash_info_file)

        try:
            self.fs.move(path, where_to_store_trashed_file)
        except IOError as e:
            self.fs.remove_file(trash_info_file)
            raise e

    def path_for_trash_info_for_file(self, path):
        path_for_trash_info = OriginalLocation(parent_realpath,
                                               self.path_maker)
        return path_for_trash_info.for_file(path)


class InfoDir:
    def __init__(self, path, fs, logger,
                 suffix):  # type: (str, RealFs, MyLogger, Suffix) -> None
        self.path = path
        self.fs = fs
        self.logger = logger
        self.suffix = suffix

    def persist_trash_info(self, basename, content):
        """
        Create a .trashinfo file in the $trash/info directory.
        returns the created TrashInfoFile.
        """

        self.fs.ensure_dir(self.path, 0o700)

        index = 0
        name_too_long = False
        while True:
            suffix = self.suffix.suffix_for_index(index)
            trashinfo_basename = create_trashinfo_basename(basename,
                                                           suffix,
                                                           name_too_long)
            trashinfo_path = os.path.join(self.path, trashinfo_basename)
            try:
                self.fs.atomic_write(trashinfo_path, content)
                self.logger.debug(".trashinfo created as %s." % trashinfo_path)
                return trashinfo_path
            except OSError as e:
                if e.errno == errno.ENAMETOOLONG:
                    name_too_long = True
                self.logger.debug(
                    "Attempt for creating %s failed." % trashinfo_path)

            index += 1


def create_trashinfo_basename(basename, suffix, name_too_long):
    after_basename = suffix + ".trashinfo"
    if name_too_long:
        truncated_basename = basename[0:len(basename) - len(after_basename)]
    else:
        truncated_basename = basename
    return truncated_basename + after_basename


class Suffix:
    def __init__(self, randint):
        self.randint = randint

    def suffix_for_index(self, index):
        if index == 0:
            return ""
        elif index < 100:
            return "_%s" % index
        else:
            return "_%s" % self.randint(0, 65535)


def format_trashinfo(original_location, deletion_date):
    content = ("[Trash Info]\n" +
               "Path=%s\n" % format_original_location(original_location) +
               "DeletionDate=%s\n" % format_date(deletion_date)).encode('utf-8')
    return content


def format_date(deletion_date):
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")


def format_original_location(original_location):
    return url_quote(original_location, '/')


class AllIsOkRules:
    def check_trash_dir_is_secure(self, trash_dir_path, fs):
        return True, []


class TopTrashDirRules:
    def check_trash_dir_is_secure(self, trash_dir_path, fs):
        parent = os.path.dirname(trash_dir_path)
        if not fs.isdir(parent):
            return False, [
                "found unusable .Trash dir (should be a dir): %s" % parent]
        if fs.islink(parent):
            return False, [
                "found unsecure .Trash dir (should not be a symlink): %s" % parent]
        if not fs.has_sticky_bit(parent):
            return False, [
                "found unsecure .Trash dir (should be sticky): %s" % parent]
        return True, []


class OriginalLocation:
    def __init__(self, parent_realpath, path_maker):
        self.parent_realpath = parent_realpath
        self.path_maker = path_maker

    def for_file(self, path):
        self.normalized_path = os.path.normpath(path)

        basename = os.path.basename(self.normalized_path)
        parent = self.parent_realpath(self.normalized_path)

        parent = self.path_maker.calc_parent_path(parent)

        return os.path.join(parent, basename)


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
