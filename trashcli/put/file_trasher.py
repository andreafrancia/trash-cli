from datetime import datetime

from typing import Callable, Dict

from trashcli.fstab import Volumes
from trashcli.put.my_logger import MyLogger
from trashcli.put.real_fs import RealFs
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.trash_result import TrashResult


class FileTrasher:

    def __init__(self,
                 fs,  # type: RealFs
                 volumes,  # type: Volumes
                 realpath,  # type: Callable[[str], str]
                 now,  # type: Callable[[], datetime]
                 trash_directories_finder,  # type: TrashDirectoriesFinder
                 parent_path,  # type: Callable[[str], str]
                 logger,  # type: MyLogger
                 reporter,  # type: TrashPutReporter
                 trash_file_in=None,  # type: TrashFileIn
                 ):  # type: (...) -> None
        self.fs = fs
        self.volumes = volumes
        self.realpath = realpath
        self.now = now
        self.trash_directories_finder = trash_directories_finder
        self.parent_path = parent_path
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
        for trash_dir_path, volume, path_maker, checker in candidates:
            file_has_been_trashed = self.trash_file_in.trash_file_in(path,
                                                                     trash_dir_path,
                                                                     volume,
                                                                     path_maker,
                                                                     checker,
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
        return self.volumes.volume_of(self.parent_path(file))
