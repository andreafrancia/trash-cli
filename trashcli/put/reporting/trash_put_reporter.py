# Copyright (C) 2007-2024 Andrea Francia Trivolzio(PV) Italy
import os
from typing import List
from typing import Tuple

from trashcli.lib.environ import Environ
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.lib.exit_codes import EX_OK
from trashcli.put.core.candidate import Candidate
from trashcli.put.core.failure_reason import FailureReason
from trashcli.put.core.failure_reason import LogContext
from trashcli.put.core.logs import Level
from trashcli.put.core.logs import LogEntry
from trashcli.put.core.logs import LogTag
from trashcli.put.core.logs import debug_str
from trashcli.put.core.logs import info_str
from trashcli.put.core.logs import log_str
from trashcli.put.core.trash_all_result import TrashAllResult
from trashcli.put.core.trashee import Trashee
from trashcli.put.describer import Describer
from trashcli.put.reporting.stats_reader import gentle_stat_read


class TrashPutReporter:
    def __init__(self,
                 describer,  # type: Describer
                 ):
        self.describer = describer

    def _describe(self, path):
        return self.describer.describe(path)

    def unable_to_trash_dot_entries(self, file
                                    ):  # type: (...) -> LogEntry
        return log_str(Level.WARNING, LogTag.trash_failed,
                       ["cannot trash %s '%s'" % (self._describe(file), file)])

    def unable_to_trash_file_non_existent(self,
                                          path,  # type: str
                                          ):  # type: (...) -> LogEntry
        return log_str(Level.WARNING, LogTag.trash_failed,
                       ["cannot trash %s '%s'" % (self._describe(path), path)])

    def unable_to_trash_file(
            self,
            trashee,  # type: Trashee
            failures,  # type: List[Tuple[Candidate, FailureReason]]
            environ,  # type: Environ
    ):  # (...) -> LogEntry
        path = trashee.path
        volume = trashee.volume
        messages = []
        messages.append("cannot trash %s '%s' (from volume '%s')" % (
            self._describe(path), path, volume))
        for candidate, reason in failures:
            context = LogContext(path, candidate, environ)
            message = " `- failed to trash %s in %s, because %s" % (
                path,
                candidate.norm_path(),
                reason.log_entries(context))
            messages.append(message)

        return log_str(Level.WARNING, LogTag.trash_failed, messages)

    @staticmethod
    def file_has_been_trashed_in_as(trashed_file,
                                    trash_dir,  # type: Candidate
                                    environ):  # type: (...) -> LogEntry
        return info_str("'%s' trashed in %s" % (trashed_file,
                                                trash_dir.shrink_user(environ)))

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

    @staticmethod
    def trash_dir_with_volume(candidate,  # type: Candidate
                              ):  # type: (...) -> LogEntry
        return debug_str("trying trash dir: %s from volume: %s" % (
            candidate.norm_path(), candidate.volume))

    @staticmethod
    def exit_code(result,  # type: TrashAllResult
                  ):  # type: (...) -> int
        if not result.any_failure():
            return EX_OK
        else:
            return EX_IOERR
