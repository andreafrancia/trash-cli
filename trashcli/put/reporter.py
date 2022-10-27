import os
import re
from grp import getgrgid
from pwd import getpwuid

from typing import List

from trashcli.put.describer import Describer
from trashcli.put.my_logger import MyLogger, LogData
from trashcli.trash import EX_IOERR, EX_OK


class TrashPutReporter:
    def __init__(self,
                 logger,  # type: MyLogger
                 describer,  # type: Describer
                 ):
        self.logger = logger
        self.describer = describer

    def describe(self, path):
        return self.describer.describe(path)

    def unable_to_trash_dot_entries(self, file, program_name):
        self.logger.warning2(
            "cannot trash %s '%s'" % (self.describe(file), file),
            program_name)

    def unable_to_trash_file(self, f, log_data):
        self.logger.warning2("cannot trash %s '%s'" % (self.describe(f), f),
                             log_data.program_name)

    def file_has_been_trashed_in_as(self,
                                    trashee,
                                    trash_directory,
                                    log_data,  # type: LogData
                                    environ):
        self.logger.info("'%s' trashed in %s" % (trashee,
                                                 shrink_user(trash_directory,
                                                             environ)),
                         log_data)

    def trash_dir_is_not_secure(self,
                                path,
                                log_data,  # type: LogData
                                ):
        self.logger.info("trash directory is not secure: %s" % path,
                         log_data)

    def log_info_messages(self,
                          messages,  # type: List[str]
                          log_data,  # type: LogData
                          ):
        for message in messages:
            self.logger.info(message, log_data)

    def log_info(self,
                 message,
                 log_data,  # type: LogData
                 ):
        self.logger.info(message, log_data)

    def wont_use_trash_dir_because_in_a_different_volume(
            self,
            path,
            norm_trash_dir_path,
            volume_of_file_to_be_trashed,
            volume_of_trash_dir,
            log_data,  # type: LogData
            environ):
        self.logger.info(
            "won't use trash dir %s because its volume (%s) in a different volume than %s (%s)"
            % (shrink_user(norm_trash_dir_path, environ), volume_of_trash_dir,
               path, volume_of_file_to_be_trashed),
            log_data)

    def unable_to_trash_file_in_because(self,
                                        file_to_be_trashed,
                                        trash_directory,
                                        error,
                                        log_data,  # type: LogData
                                        environ):
        self.logger.info("failed to trash %s in %s, because: %s" % (
            file_to_be_trashed, shrink_user(trash_directory, environ), error),
                         log_data)
        self.logger.debug_func_result(
            lambda: self.log_data_for_debugging(error), log_data)

    @classmethod
    def log_data_for_debugging(cls, error):
        try:
            filename = error.filename
        except AttributeError:
            pass
        else:
            if filename is not None:
                for path in [filename, os.path.dirname(filename)]:
                    info = gentle_stat_read(path)
                    yield "stats for %s: %s" % (path, info)

    def trash_dir_with_volume(self, trash_dir_path, volume_path,
                              log_data, # type: LogData
                              ):
        self.logger.info(
            "trying trash dir: %s from volume: %s" % (trash_dir_path,
                                                      volume_path),
            log_data)

    def exit_code(self, result):
        if not result.some_file_has_not_be_trashed:
            return EX_OK
        else:
            return EX_IOERR

    def volume_of_file(self, volume, log_data):
        self.logger.info("volume of file: %s" % volume, log_data)


def gentle_stat_read(path):
    try:
        stats = os.lstat(path)
        user = getpwuid(stats.st_uid).pw_name
        group = getgrgid(stats.st_gid).gr_name
        perms = remove_octal_prefix(oct(stats.st_mode & 0o777))
        return "%s %s %s" % (perms, user, group)
    except OSError as e:
        return str(e)


def remove_octal_prefix(s):
    remove_new_octal_format = s.replace('0o', '')
    remove_old_octal_format = re.sub(r"^0", '', remove_new_octal_format)
    return remove_old_octal_format


def shrink_user(path, environ):
    import posixpath
    import re
    try:
        home_dir = environ.get('HOME', '')
        home_dir = posixpath.normpath(home_dir)
        if home_dir != '':
            path = re.sub('^' + re.escape(home_dir + os.path.sep),
                          '~' + os.path.sep, path)
    except KeyError:
        pass
    return path
