import datetime
import os

from six import binary_type
from six import text_type

from tests.support.restore.a_trashed_file import ATrashedFile
from trashcli.put.format_trash_info import format_trashinfo
from trashcli.put.fs.fs import Fs


class TrashDirFixture:
    def __init__(self,
                 fs,  # type: Fs
                 trash_dir_path,  # type: text_type
                 ):
        self.fs = fs
        self.trash_dir_path = trash_dir_path
        self.counter = 0

    def add_trashed_file(self, path):
        self.add_trash_file(path,
                            datetime.datetime(1970,1,1),
                            "contents of %s" % path
                            )

    def add_trash_file(self,
                       from_path,
                       time,
                       original_file_content,  # type: binary_type
                       ):
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path) + ("_%s" % self.counter if self.counter > 0 else "")
        self.counter = self.counter + 1
        info_path = os.path.join(self.trash_dir_path, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(self.trash_dir_path, 'files', basename)
        self.fs.make_file_p(info_path, content)
        self.fs.make_file_p(backup_copy_path, original_file_content)

    def make_trashed_file(self,
                          from_path,
                          time,
                          original_file_content,  # type: binary_type
                          ):  # type: (...) -> ATrashedFile
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path)
        info_path = os.path.join(self.trash_dir_path, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(self.trash_dir_path, 'files', basename)
        trashed_file = ATrashedFile(trashed_from=from_path,
                                    info_file=info_path,
                                    backup_copy=backup_copy_path)
        self.fs.make_file_p(info_path, content)
        self.fs.make_file_p(backup_copy_path, original_file_content)
        return trashed_file
