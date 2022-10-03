import errno
import os

from trashcli.put.my_logger import MyLogger
from trashcli.put.real_fs import RealFs
from trashcli.put.suffix import Suffix


class InfoDir:
    def __init__(self,
                 fs,  # type: RealFs
                 logger,  # type: MyLogger
                 suffix,  # type: Suffix
                 ):  # type: (...) -> None
        self.fs = fs
        self.logger = logger
        self.suffix = suffix

    def persist_trash_info(self, basename, content, program_name, verbose,
                           info_dir_path):
        """
        Create a .trashinfo file in the $trash/info directory.
        returns the created TrashInfoFile.
        """

        self.fs.ensure_dir(info_dir_path, 0o700)

        index = 0
        name_too_long = False
        while True:
            suffix = self.suffix.suffix_for_index(index)
            trashinfo_basename = create_trashinfo_basename(basename,
                                                           suffix,
                                                           name_too_long)
            trashinfo_path = os.path.join(info_dir_path, trashinfo_basename)
            try:
                self.fs.atomic_write(trashinfo_path, content)
                self.logger.debug(".trashinfo created as %s." % trashinfo_path,
                                  program_name, verbose)
                return trashinfo_path
            except OSError as e:
                if e.errno == errno.ENAMETOOLONG:
                    name_too_long = True
                self.logger.debug(
                    "attempt for creating %s failed." % trashinfo_path,
                    program_name, verbose)

            index += 1


def create_trashinfo_basename(basename, suffix, name_too_long):
    after_basename = suffix + ".trashinfo"
    if name_too_long:
        truncated_basename = basename[0:len(basename) - len(after_basename)]
    else:
        truncated_basename = basename
    return truncated_basename + after_basename
