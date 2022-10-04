import os
from grp import getgrgid
from pwd import getpwuid

from typing import Dict

from trashcli.put.describe import describe
from trashcli.put.my_logger import MyLogger
from trashcli.trash import EX_IOERR, EX_OK


class TrashPutReporter:
    def __init__(self, logger):  # type: (MyLogger) -> None
        self.logger = logger
        self.no_argument_specified = False

    def unable_to_trash_dot_entries(self, file, program_name):
        self.logger.warning2("cannot trash %s '%s'" % (describe(file), file),
                             program_name)

    def unable_to_trash_file(self, f, program_name):
        self.logger.warning2("cannot trash %s '%s'" % (describe(f), f),
                             program_name)

    def file_has_been_trashed_in_as(self, trashee, trash_directory,
                                    program_name, verbose, environ):
        self.logger.info("'%s' trashed in %s" % (trashee,
                                                 shrink_user(trash_directory,
                                                             environ)),
                         program_name, verbose)

    def trash_dir_is_not_secure(self, path, program_name, verbose):
        self.logger.info("trash directory %s is not secure" % path,
                         program_name, verbose)

    def log_info(self, message, program_name, verbose):
        self.logger.info(message, program_name, verbose)

    def wont_use_trash_dir_because_in_a_different_volume(
            self,
            path,
            norm_trash_dir_path,
            volume_of_file_to_be_trashed,
            volume_of_trash_dir,
            program_name, verbose,
            environ):
        self.logger.info(
            "won't use trash dir %s because its volume (%s) in a different volume than %s (%s)"
            % (shrink_user(norm_trash_dir_path, environ), volume_of_trash_dir,
               path, volume_of_file_to_be_trashed),
            program_name, verbose)

    def unable_to_trash_file_in_because(self,
                                        file_to_be_trashed,
                                        trash_directory,
                                        error,
                                        program_name, verbose, environ):
        self.logger.info("failed to trash %s in %s, because: %s" % (
            file_to_be_trashed, shrink_user(trash_directory, environ), error),
                         program_name, verbose)
        self.logger.debug_func_result(
            lambda: self.log_data_for_debugging(error),
            program_name, verbose)

    @classmethod
    def log_data_for_debugging(cls, error):
        try:
            filename = error.filename
        except AttributeError:
            pass
        else:
            if filename is not None:
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

    def trash_dir_with_volume(self, trash_dir_path, volume_path, program_name,
                              verbose):
        self.logger.info(
            "trying trash dir: %s from volume: %s" % (trash_dir_path,
                                                      volume_path),
            program_name, verbose)

    def exit_code(self, result):
        if not result.some_file_has_not_be_trashed:
            return EX_OK
        else:
            return EX_IOERR

    def volume_of_file(self, volume, program_name, verbose):
        self.logger.info("volume of file: %s" % volume, program_name, verbose)


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
