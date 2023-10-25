import errno
import os

from typing import Optional, NamedTuple, Tuple

from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.put.candidate import Candidate
from trashcli.put.clock import PutClock
from trashcli.put.format_trash_info import format_trashinfo
from trashcli.put.fs.fs import Fs
from trashcli.put.my_logger import LogData
from trashcli.put.my_logger import MyLogger
from trashcli.put.original_location import OriginalLocation
from trashcli.put.suffix import Suffix


class TrashinfoData(NamedTuple('TrashinfoData', [
    ('basename', str),
    ('content', str),
    ('log_data', LogData),
    ('info_dir_path', str),
])):
    pass


class TrashedFile(NamedTuple('Paths', [
    ('trashinfo_path', str),
])):
    @property
    def backup_copy_path(self):  # type: () -> str
        return path_of_backup_copy(self.trashinfo_path)


class PersistingInfoDir:
    def __init__(self,
                 fs,  # type: Fs
                 logger,  # type: MyLogger
                 suffix,  # type: Suffix
                 ):  # type: (...) -> None
        self.fs = fs
        self.logger = logger
        self.suffix = suffix

    def persist_trash_info(self,
                           data,  # type: TrashinfoData
                           ):
        """
        Create a .trashinfo file in the $trash/info directory.
        returns the created TrashInfoFile.
        """

        index = -1
        name_too_long = False
        while True:
            index += 1

            suffix = self.suffix.suffix_for_index(index)
            trashinfo_basename = create_trashinfo_basename(data.basename,
                                                           suffix,
                                                           name_too_long)
            trashinfo_path = os.path.join(data.info_dir_path,
                                          trashinfo_basename)
            if os.path.exists(path_of_backup_copy(trashinfo_path)):
                continue
            try:
                self.fs.atomic_write(trashinfo_path, data.content)
                self.logger.debug(".trashinfo created as %s." % trashinfo_path,
                                  data.log_data)
                return TrashedFile(trashinfo_path)
            except OSError as e:
                if e.errno == errno.ENAMETOOLONG:
                    name_too_long = True
                self.logger.debug(
                    "attempt for creating %s failed." % trashinfo_path,
                    data.log_data)


class InfoDir2:
    def __init__(self,
                 persister,  # type: PersistingInfoDir
                 original_location,  # type: OriginalLocation
                 clock,  # type: PutClock
                 ):
        self.persister = persister
        self.original_location = original_location
        self.clock = clock

    def create_trashinfo_file(self,
                              trashinfo_data, # type: TrashinfoData
                              ):  # type: (...) -> Tuple[bool, Optional[TrashedFile], Optional[Exception]]
        try:
            trashed_file = self.persister.persist_trash_info(trashinfo_data)
            return True, trashed_file, None
        except (IOError, OSError) as error:
            return False, None, error

    def make_trashinfo_data(self,
                            path,  # type: str
                            candidate,  # type: Candidate
                            log_data,  # type: LogData
                            ):  # type: (...) -> Tuple[bool, Optional[TrashinfoData], Optional[Exception]]
        try:
            original_location = self.original_location.for_file(path,
                                                                candidate.path_maker_type,
                                                                candidate.volume)
            content = format_trashinfo(original_location, self.clock.now())
            basename = os.path.basename(original_location)
            trash_info_data = TrashinfoData(basename, content, log_data,
                                            candidate.info_dir())
            return True, trash_info_data, None
        except (IOError, OSError) as error:
            return False, None, error


def create_trashinfo_basename(basename, suffix, name_too_long):
    after_basename = suffix + ".trashinfo"
    if name_too_long:
        truncated_basename = basename[0:len(basename) - len(after_basename)]
    else:
        truncated_basename = basename
    return truncated_basename + after_basename
