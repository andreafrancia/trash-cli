from datetime import datetime

from typing import Callable, Dict

from trashcli.fstab import Volumes
from trashcli.put.my_logger import MyLogger
from trashcli.put.parent_realpath import ParentRealpath
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.trash_result import TrashResult


class FileTrasher:

    def __init__(self,
                 volumes,  # type: Volumes
                 trash_directories_finder,  # type: TrashDirectoriesFinder
                 parent_realpath,  # type: ParentRealpath
                 logger,  # type: MyLogger
                 reporter,  # type: TrashPutReporter
                 trash_file_in=None,  # type: TrashFileIn
                 ):  # type: (...) -> None
        self.volumes = volumes
        self.trash_directories_finder = trash_directories_finder
        self.parent_realpath = parent_realpath
        self.logger = logger
        self.reporter = reporter
        self.trash_file_in = trash_file_in

    def trash_file(self,
                   path,  # type: str
                   forced_volume,
                   user_trash_dir,
                   result,  # type: TrashResult
                   environ,  # type: Dict[str, str]
                   uid,  # type: int
                   program_name,  # type: str
                   verbose,  # type: int
                   ):
        volume_of_file_to_be_trashed = forced_volume or \
                                       self.volume_of_parent(path)
        candidates = self.trash_directories_finder. \
            possible_trash_directories_for(volume_of_file_to_be_trashed,
                                           user_trash_dir, environ, uid)
        self.reporter.volume_of_file(volume_of_file_to_be_trashed, program_name,
                                     verbose)
        file_has_been_trashed = False
        for candidate in candidates:
            file_has_been_trashed = \
                self.trash_file_in.trash_file_in(path,
                                                 candidate,
                                                 file_has_been_trashed,
                                                 volume_of_file_to_be_trashed,
                                                 program_name,
                                                 verbose,
                                                 environ)
            if file_has_been_trashed: break

        if not file_has_been_trashed:
            result = result.mark_unable_to_trash_file()
            self.reporter.unable_to_trash_file(path, program_name)

        return result

    def volume_of_parent(self, file):
        return self.volumes.volume_of(
            self.parent_realpath.parent_realpath(file))
