# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy

from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.environ import Environ
from trashcli.put.core.trash_result import TrashResult
from trashcli.put.fs.parent_realpath import ParentRealpathFs
from trashcli.put.fs.volume_of_parent import VolumeOfParent
from trashcli.put.my_logger import MyLogger, LogData
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_file_in import Janitor
from trashcli.put.trashee import Trashee


class FileTrasher:

    def __init__(self,
                 volumes,  # type: VolumeOf
                 trash_directories_finder,  # type: TrashDirectoriesFinder
                 parent_realpath_fs,  # type: ParentRealpathFs
                 logger,  # type: MyLogger
                 reporter,  # type: TrashPutReporter
                 janitor,  # type: Janitor
                 volume_of_parent,  # type: VolumeOfParent
                 ):  # type: (...) -> None
        self.volumes = volumes
        self.trash_directories_finder = trash_directories_finder
        self.parent_realpath_fs = parent_realpath_fs
        self.logger = logger
        self.reporter = reporter
        self.janitor = janitor
        self.volume_of_parent = volume_of_parent or volume_of_parent

    def trash_file(self,
                   path,  # type: str
                   forced_volume,
                   user_trash_dir,
                   home_fallback,
                   environ,  # type: Environ
                   uid,  # type: int
                   log_data,  # type: LogData
                   ):
        volume = self._figure_out_volume(path, forced_volume)
        file_be_trashed = Trashee(path, volume)
        candidates = self._select_candidates(volume, user_trash_dir, environ,
                                             uid, home_fallback)
        self.reporter.volume_of_file(volume, log_data)
        file_has_been_trashed = False
        for candidate in candidates:
            file_has_been_trashed, log = self.janitor.trash_file_in(candidate,
                                                                    log_data,
                                                                    environ,
                                                                    file_be_trashed)
            if file_has_been_trashed:
                self.reporter.file_has_been_trashed_in_as(path,
                                                          candidate,
                                                          log_data,
                                                          environ)
                break
            else:
                self.reporter.report_reason(log, log_data, environ,
                                            file_be_trashed, candidate)

        if not file_has_been_trashed:
            self.reporter.unable_to_trash_file(path, log_data)
            return TrashResult.Failure

        return TrashResult.Success

    def _figure_out_volume(self, path, default_volume):
        if default_volume:
            return default_volume
        else:
            return self.volume_of_parent.volume_of_parent(path)

    def _select_candidates(self, volume, user_trash_dir, environ, uid,
                           home_fallback):
        return self.trash_directories_finder. \
            possible_trash_directories_for(volume,
                                           user_trash_dir, environ, uid,
                                           home_fallback)
