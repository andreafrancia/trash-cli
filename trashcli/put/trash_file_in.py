import os

from trashcli.put.candidate import Candidate
from trashcli.put.dir_maker import DirMaker
from trashcli.put.file_to_be_trashed import FileToBeTrashed
from trashcli.put.fs import Fs
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import LogData
from trashcli.put.path_maker import PathMaker
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.security_check import SecurityCheck
from trashcli.put.trash_dir_volume import TrashDirVolume
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut


class TrashFileIn:
    def __init__(self,
                 fs,  # type: Fs
                 reporter,  # type: TrashPutReporter
                 info_dir,  # type: InfoDir
                 trash_dir,  # type: TrashDirectoryForPut
                 trash_dir_volume,  # type: TrashDirVolume
                 dir_maker,  # type: DirMaker
                 ):
        self.reporter = reporter
        self.path_maker = PathMaker()
        self.security_check = SecurityCheck(fs)
        self.info_dir = info_dir
        self.trash_dir = trash_dir
        self.trash_dir_volume = trash_dir_volume
        self.dir_maker = dir_maker

    def trash_file_in(self,
                      candidate,  # type: Candidate
                      log_data,  # type: LogData
                      environ,
                      file_to_be_trashed,  # type: FileToBeTrashed
                      ):  # type: (...) -> bool
        file_has_been_trashed = False
        path = file_to_be_trashed.path
        trash_dir_path = candidate.trash_dir_path
        norm_trash_dir_path = os.path.normpath(trash_dir_path)
        trash_dir_is_secure, messages = self.security_check. \
            check_trash_dir_is_secure(norm_trash_dir_path,
                                      candidate.check_type)
        self.reporter.log_info_messages(messages, log_data)

        if trash_dir_is_secure:
            volume_of_trash_dir = self.trash_dir_volume. \
                volume_of_trash_dir(trash_dir_path)
            self.reporter.trash_dir_with_volume(candidate, log_data)
            if self._file_could_be_trashed_in(
                    file_to_be_trashed.volume,
                    volume_of_trash_dir):
                try:
                    info_dir_path = os.path.join(trash_dir_path, 'info')
                    self.dir_maker.mkdir_p(trash_dir_path, 0o700)
                    self.dir_maker.mkdir_p(candidate.files_dir(), 0o700)
                    self.dir_maker.mkdir_p(candidate.info_dir(), 0o700)

                    self.trash_dir.trash2(path,
                                          log_data,
                                          candidate.path_maker_type,
                                          candidate.volume,
                                          info_dir_path)
                    self.reporter.file_has_been_trashed_in_as(path,
                                                              candidate,
                                                              log_data,
                                                              environ)
                    file_has_been_trashed = True

                except (IOError, OSError) as error:
                    self.reporter.unable_to_trash_file_in_because(
                        path, norm_trash_dir_path, error, log_data,
                        environ)
            else:
                self.reporter.wont_use_trash_dir_because_in_a_different_volume(
                    file_to_be_trashed, log_data, environ, candidate)
        else:
            self.reporter.trash_dir_is_not_secure(norm_trash_dir_path, log_data)
        return file_has_been_trashed

    def _file_could_be_trashed_in(self,
                                  volume_of_file_to_be_trashed,
                                  volume_of_trash_dir):
        return volume_of_trash_dir == volume_of_file_to_be_trashed
