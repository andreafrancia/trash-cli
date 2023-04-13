import errno
import os

from trashcli.put.fs.fs import Fs
from trashcli.put.my_logger import MyLogger, LogData
from trashcli.put.suffix import Suffix
from trashcli.trash import path_of_backup_copy


class InfoDir:
    def __init__(self,
                 fs,  # type: Fs
                 logger,  # type: MyLogger
                 suffix,  # type: Suffix
                 ):  # type: (...) -> None
        self.fs = fs
        self.logger = logger
        self.suffix = suffix

    def persist_trash_info(self,
                           basename, #type: str
                           content, #type: str
                           log_data, #type: LogData
                           info_dir_path, #type: str
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
            trashinfo_basename = create_trashinfo_basename(basename,
                                                           suffix,
                                                           name_too_long)
            trashinfo_path = os.path.join(info_dir_path, trashinfo_basename)
            if os.path.exists(path_of_backup_copy(trashinfo_path)):
                continue
            try:
                self.fs.atomic_write(trashinfo_path, content)
                self.logger.debug(".trashinfo created as %s." % trashinfo_path,
                                  log_data)
                return trashinfo_path
            except OSError as e:
                if e.errno == errno.ENAMETOOLONG:
                    name_too_long = True
                self.logger.debug(
                    "attempt for creating %s failed." % trashinfo_path,
                    log_data)



def create_trashinfo_basename(basename, suffix, name_too_long):
    after_basename = suffix + ".trashinfo"
    if name_too_long:
        truncated_basename = basename[0:len(basename) - len(after_basename)]
    else:
        truncated_basename = basename
    return truncated_basename + after_basename
