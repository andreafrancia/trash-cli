# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import re
from pwd import getpwuid
from typing import List
from typing import Tuple

from grp import getgrgid

from trashcli.lib.environ import Environ
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.lib.exit_codes import EX_OK
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.failure_reason import FailureReason
from trashcli.put.core.failure_reason import LogContext
from trashcli.put.core.trash_all_result import TrashAllResult
from trashcli.put.core.trashee import Trashee
from trashcli.put.describer import Describer
from trashcli.put.my_logger import LogData
from trashcli.put.my_logger import MyLogger


class TrashPutReporter:
    def __init__(self,
                 logger,  # type: MyLogger
                 describer,  # type: Describer
                 ):
        self.logger = logger
        self.describer = describer

    def _describe(self, path):
        return self.describer.describe(path)

    def unable_to_trash_dot_entries(self, file, program_name):
        self.logger.warning2(
            "cannot trash %s '%s'" % (self._describe(file), file),
            program_name)

    def unable_to_trash_file_non_existent(self,
                                          path,  # type: str
                                          log_data, # type: LogData
                                          ):
        self.logger.warning2("cannot trash %s '%s'" % (
            self._describe(path), path), log_data.program_name)

    # TODO
    def unable_to_trash_file2(self,
                              trashee,  # type: Trashee
                              log_data,  # type: LogData
                              failures,
                              # type: List[Tuple[Candidate, FailureReason]]
                              environ,  # type: Environ
                              ):
        path = trashee.path
        volume = trashee.volume
        self.logger.warning2("cannot trash %s '%s' (from volume '%s')" % (
            self._describe(path), path, volume), log_data.program_name)
        for candidate, reason in failures:
            context = LogContext(path, candidate, environ)
            message = " `- failed to trash %s in %s, because %s" % (
                path,
                candidate.norm_path(),
                reason.log_entries(context))
            self.logger.warning2(message, log_data.program_name)

    def file_has_been_trashed_in_as(self,
                                    trashed_file,
                                    trash_dir,  # type: Candidate
                                    log_data,  # type: LogData
                                    environ):
        trash_dir_path = trash_dir.shrink_user(environ)
        self.logger.info("'%s' trashed in %s" % (trashed_file, trash_dir_path),
                         log_data)

    def log_info_messages(self,
                          messages,  # type: List[str]
                          log_data,  # type: LogData
                          ):
        for message in messages:
            self.logger.info(message, log_data)

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

    def trash_dir_with_volume(self,
                              candidate,  # type: Candidate
                              log_data,  # type: LogData
                              ):
        # type: (...) -> None
        self.logger.debug(
            "trying trash dir: %s from volume: %s" % (candidate.norm_path(),
                                                      candidate.volume),
            log_data)

    def exit_code(self,
                  result,  # type: TrashAllResult
                  ):  # type: (...) -> int
        if not result.any_failure():
            return EX_OK
        else:
            return EX_IOERR

    def report_reason(self,
                      reason,  # type: FailureReason
                      log_data,  # type: LogData
                      environ,  # type: Environ
                      trashee_path,  # type: str
                      candidate,  # type: Candidate
                      ):  # type: (...) -> None
        context = LogContext(trashee_path, candidate, environ)
        self.logger.info(reason.log_entries(context), log_data)


def gentle_stat_read(path):
    try:
        stats = os.lstat(path)
        user = getpwuid(stats.st_uid).pw_name
        group = getgrgid(stats.st_gid).gr_name
        perms = remove_octal_prefix(oct(stats.st_mode & 0o777))
        return "%s %s %s" % (perms, user, group)
    except OSError as e:
        return str(e)


def remove_octal_prefix(s):  # type: (str) -> str
    remove_new_octal_format = s.replace('0o', '')
    remove_old_octal_format = re.sub(r"^0", '', remove_new_octal_format)
    return remove_old_octal_format
