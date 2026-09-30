import os

from tests.support.restore.a_trashed_file import ATrashedFile
from trashcli.fslib.protocols.fs import Fs
from trashcli.put.format_trash_info import format_trashinfo


class RestoreFixture:
    def __init__(self,
                 fs,  # type: Fs
                 ):
        self.fs = fs

    def make_trashed_file(self, from_path, trash_dir, time,
                          original_file_content):
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path)
        info_path = os.path.join(trash_dir, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(trash_dir, 'files', basename)
        trashed_file = ATrashedFile(trashed_from=from_path,
                                    info_file=info_path,
                                    backup_copy=backup_copy_path)
        self.add_file(info_path, content)
        self.add_file(backup_copy_path, original_file_content.encode('utf-8'))
        return trashed_file

    def add_trash_file(self, from_path, trash_dir, time,
                       original_file_content=''):
        content = format_trashinfo(from_path, time)
        basename = os.path.basename(from_path)
        info_path = os.path.join(trash_dir, 'info', "%s.trashinfo" % basename)
        backup_copy_path = os.path.join(trash_dir, 'files', basename)
        self.add_file(info_path, content)
        self.add_file(backup_copy_path, original_file_content.encode('utf-8'))

    def add_trash_empty_file(self, from_path, trash_dir, time):
        self.add_trash_file(from_path, trash_dir, time, '')

    def add_file(self, path, content=b''):
        self.fs.makedirs(os.path.dirname(path), 0o755)
        self.fs.make_file(path, content)
