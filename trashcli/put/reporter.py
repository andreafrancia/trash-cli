import os
from grp import getgrgid
from pwd import getpwuid

from typing import Dict

from trashcli.put.describe import describe
from trashcli.put.my_logger import MyLogger
from trashcli.trash import EX_OK, EX_IOERR


class TrashPutReporter:
    def __init__(self, logger,
                 environ):  # type: (MyLogger, Dict[str, str]) -> None
        self.logger = logger
        self.no_argument_specified = False
        self.environ = environ

    def unable_to_trash_dot_entries(self, file):
        self.logger.warning2("cannot trash %s '%s'" % (describe(file), file))

    def unable_to_trash_file(self, f):
        self.logger.warning2("cannot trash %s '%s'" % (describe(f), f))

    def file_has_been_trashed_in_as(self, trashee, trash_directory):
        self.logger.info("'%s' trashed in %s" % (trashee,
                                                 shrink_user(trash_directory,
                                                             self.environ)))

    def trash_dir_is_not_secure(self, path):
        self.logger.info("trash directory %s is not secure" % path)

    def log_info(self, message):
        self.logger.info(message)

    def unable_to_trash_file_in_because(self,
                                        file_to_be_trashed,
                                        trash_directory, error):
        self.logger.info("Failed to trash %s in %s, because: %s" % (
            file_to_be_trashed, shrink_user(trash_directory,
                                            self.environ), error))
        self.logger.debug_func_result(
            lambda: self.log_data_for_debugging(error))

    @classmethod
    def log_data_for_debugging(cls, error):
        try:
            filename = error.filename
        except AttributeError:
            pass
        else:
            for path in [filename, os.path.dirname(filename)]:
                info = cls.get_stats(path)
                yield "stats for %s: %s" % (path, info)

    @staticmethod
    def get_stats(path):
        try:
            stats = os.stat(path, follow_symlinks=False)
            user = getpwuid(stats.st_uid).pw_name
            group = getgrgid(stats.st_gid).gr_name
            perms = oct(stats.st_mode & 0o777).replace('0o', '')
            return "%s %s %s" % (perms, user, group)
        except OSError as e:
            return str(e)

    def trash_dir_with_volume(self, trash_dir_path, volume_path):
        self.logger.info("Trash-dir: %s from volume: %s" % (trash_dir_path,
                                                            volume_path))

    def exit_code(self, result):
        if not result.some_file_has_not_be_trashed:
            return EX_OK
        else:
            return EX_IOERR

    def volume_of_file(self, volume):
        self.logger.info("Volume of file: %s" % volume)


def shrink_user(path, environ):
    import posixpath
    import re
    try:
        home_dir = environ['HOME']
        home_dir = posixpath.normpath(home_dir)
        if home_dir != '':
            path = re.sub('^' + re.escape(home_dir + os.path.sep),
                          '~' + os.path.sep, path)
    except KeyError:
        pass
    return path
