import sys
from typing import TypeVar

from six import StringIO

from tests.support.cmd.capture_exit_code2 import capture_exit_code2
from tests.support.dirs.my_path import MyPath
from tests.support.fakes.fake_trash_dir import FakeTrashDir
from tests.support.py2mock import Mock
from tests.test_restore.support.capture_logger import CaptureLogger
from trashcli.fslib.real_fs_operations import RealListFilesInDir, RealExists, RealIsStickyDir, RealIsSymLink, \
    RealIsWorldWritable
from trashcli.fstab.volumes import FakeVolumes
from trashcli.lib.my_input import HardCodedInput
from trashcli.restore.real_restore_fs import RealRestoreWriterFs, \
    RealPathReaderFs, RealFileReaderFs
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.restore.restore_fs import RestoreReadFs
from trashcli.restore.trashed_files import TrashedFiles
from trashcli.trash_dirs_scanner import TopTrashDirRulesFs


class AlmostFakeRestoreReadFs(FakeVolumes,
                              RestoreReadFs,
                              TopTrashDirRulesFs,
                              ):
    def __init__(self, cwd, volumes):
        super().__init__(volumes)
        self.cwd = cwd

    def getcwd_as_realpath(self):  # type: () -> str
        return self.cwd

    list_files_in_dir = RealListFilesInDir().list_files_in_dir
    path_exists = RealPathReaderFs().path_exists
    path_lexists = RealPathReaderFs().path_lexists
    path_isdir = RealPathReaderFs().path_isdir
    contents_of = RealFileReaderFs().contents_of
    exists = RealExists().exists
    is_sticky_dir = RealIsStickyDir().is_sticky_dir
    is_symlink = RealIsSymLink().is_symlink
    is_world_writable = RealIsWorldWritable().is_world_writable
