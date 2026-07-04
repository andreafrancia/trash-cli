import errno
import os
from typing import NamedTuple, Iterator

from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.put.core.either import Right, Left, Either
from trashcli.put.core.failure_reason import FailureReason, LogContext
from trashcli.put.fs.fs import Fs
from trashcli.put.janitor_tools.permanent_write_errnos import HARD_ERRNOS
from trashcli.put.jobs import JobStatus, NeedsMoreAttempts, Succeeded, \
    JobExecutor
from trashcli.put.my_logger import LogData, MyLogger
from trashcli.put.suffix import Suffix


class TrashinfoData(NamedTuple('TrashinfoData', [
    ('basename', str),
    ('content', str),
    ('info_dir_path', str),
])):
    pass


class TrashedFile(NamedTuple('TrashedFile', [
    ('trashinfo_path', str),
])):
    @property
    def backup_copy_path(self):  # type: () -> str
        return path_of_backup_copy(self.trashinfo_path)

class UnableToPersistTrashinfo(FailureReason):
    def __init__(self, error):
        self.error = error

    def log_entries(self, context):  # type: (LogContext) -> str
        return "failed to create trashinfo file: %s" % self.error

class InfoFilePersister:
    def __init__(self,
                 fs,  # type: Fs
                 logger,  # type: MyLogger
                 suffix,  # type: Suffix
                 ):  # type: (...) -> None
        self.fs = fs
        self.logger = logger
        self.suffix = suffix

    def persist(self,
                trashinfo_data,  # type: TrashinfoData
                log_data,  # type: LogData
                ):  # type: (...) -> Either[TrashedFile, UnableToPersistTrashinfo]
        try:
            trashed_file: TrashedFile = self._persist_trash_info(
                trashinfo_data, log_data
            )
            return Right(trashed_file)
        except OSError as e:
            return Left(UnableToPersistTrashinfo(e))


    def _persist_trash_info(self,
                            trashinfo_data,  # type: TrashinfoData
                            log_data,  # type: LogData
                            ):  # type: (...) -> TrashedFile
        job_executor = JobExecutor(self.logger, TrashedFile)
        persisting_job = self._try_persist(trashinfo_data)
        return job_executor.execute(persisting_job, log_data)

    Result = Iterator[JobStatus[TrashedFile]]

    def _try_persist(self,
                     data,  # type: TrashinfoData
                     ):  # type: (...) -> Result
        index = 0
        name_too_long = False
        # No arbitrary cap: a permanent write error (see HARD_ERRNOS) stops the loop.
        while True:
            suffix = self.suffix.suffix_for_index(index)
            trashinfo_basename = create_trashinfo_basename(data.basename,
                                                           suffix,
                                                           name_too_long)
            trashinfo_path = os.path.join(data.info_dir_path,
                                          trashinfo_basename)
            if os.path.exists(path_of_backup_copy(trashinfo_path)):
                index += 1
                continue
            try:
                self.fs.atomic_write(trashinfo_path, data.content)
                yield Succeeded(TrashedFile(trashinfo_path),
                                ".trashinfo created as %s." % trashinfo_path)
                return
            except OSError as e:
                if e.errno == errno.ENAMETOOLONG:
                    name_too_long = True
                elif e.errno in HARD_ERRNOS:
                    raise
                yield NeedsMoreAttempts(trashinfo_path,
                                        "attempt for creating %s failed." % trashinfo_path)

            index += 1


def create_trashinfo_basename(basename, suffix, name_too_long):
    after_basename = suffix + ".trashinfo"
    if name_too_long:
        truncated_basename = basename[0:len(basename) - len(after_basename)]
    else:
        truncated_basename = basename
    return truncated_basename + after_basename
