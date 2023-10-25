from typing import Optional

from trashcli.put.fs.fs import Fs
from trashcli.put.info_dir import InfoDir2
from trashcli.put.info_dir import TrashedFile


class TrashDirectoryForPut:
    def __init__(self,
                 fs,  # type: Fs
                 info_dir2,  # type: InfoDir2
                 ):
        self.fs = fs
        self.info_dir2 = info_dir2

    def try_trash(self,
                  path,  # type: str
                  paths,  # type: TrashedFile
                  ):  # type: (...) -> Optional[Exception]
        try:
            self.fs.move(path, paths.backup_copy_path)
            return None
        except (IOError, OSError) as error:
            self.fs.remove_file(paths.trashinfo_path)
            return error
