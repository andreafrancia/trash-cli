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

_TrashinfoDataFields = NamedTuple('_TrashinfoDataFields', [
    ('basename', str),
    ('content', str),
    ('info_dir_path', str),
])

class TrashinfoData(_TrashinfoDataFields):
    @property
    def info_full_path(self):
        return os.path.join(self.info_dir_path, self.basename)
    @property
    def original_file_path(self):
        return path_of_backup_copy(self.info_full_path)


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

    def reserve_name(self,
                     data,  # type: TrashinfoData
                     ):  # type: (...) -> Either[TrashedFile, UnableToPersistTrashinfo]
        index = 0
        while True:
            suffix = self.suffix.suffix_for_index(index)
            trashinfo_basename = create_trashinfo_basename(data.basename,
                                                           suffix,
                                                           False)
            trashinfo_path = os.path.join(data.info_dir_path,
                                          trashinfo_basename)
            if os.path.exists(path_of_backup_copy(trashinfo_path)):
                index += 1
                continue
            return Right(TrashedFile(trashinfo_path))

    def persist(self,
                trashed_file,  # type: TrashedFile
                trashinfo_data,  # type: TrashinfoData
                log_data,  # type: LogData
                ):  # type: (...) -> Either[TrashedFile, UnableToPersistTrashinfo]
        try:
            written_file = self._write_trash_info(
                trashed_file, trashinfo_data, log_data
            )
            return Right(written_file)
        except OSError as e:
            return Left(UnableToPersistTrashinfo(e))

    def _write_trash_info(self,
                          trashed_file,  # type: TrashedFile
                          trashinfo_data,  # type: TrashinfoData
                          log_data,  # type: LogData
                          ):  # type: (...) -> TrashedFile
        job_executor = JobExecutor(self.logger, TrashedFile)
        persisting_job = self._try_write(trashed_file, trashinfo_data)
        return job_executor.execute(persisting_job, log_data)

    Result = Iterator[JobStatus[TrashedFile]]

    def _try_write(self,
                   trashed_file,  # type: TrashedFile
                   data,  # type: TrashinfoData
                   ):  # type: (...) -> Result
        index = 0
        name_too_long = False
        backup_copy_path = trashed_file.backup_copy_path
        # No arbitrary cap: a permanent write error (see HARD_ERRNOS) stops the loop.
        while True:
            suffix = self.suffix.suffix_for_index(index)
            trashinfo_basename = create_trashinfo_basename(data.basename,
                                                           suffix,
                                                           name_too_long)
            trashinfo_path = os.path.join(data.info_dir_path,
                                          trashinfo_basename)
            if backup_copy_path != path_of_backup_copy(trashinfo_path):
                # The file is already in the trash: keep its name in sync
                # with the trashinfo name.
                if os.path.exists(path_of_backup_copy(trashinfo_path)):
                    index += 1
                    continue
                if self.fs.lexists(backup_copy_path):
                    self.fs.move(backup_copy_path,
                                 path_of_backup_copy(trashinfo_path))
                backup_copy_path = path_of_backup_copy(trashinfo_path)
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
