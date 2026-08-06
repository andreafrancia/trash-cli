from trashcli.fslib.real_fs_operations import RealListFilesInDir, RealExists, RealIsSymLink, \
    RealIsWorldWritable
from trashcli.fslib.real_is_sticky_dir import RealIsStickyDir
from trashcli.fstab.fake.fake_volumes import FakeVolumes
from trashcli.restore.real_fs.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.real_fs.real_file_reader_fs import RealFileReaderFs
from trashcli.restore.fs.restore_read_fs import RestoreReadFs
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
    exists = RealExists().path_exists
    is_sticky_dir = RealIsStickyDir().is_sticky_dir
    is_symlink = RealIsSymLink().is_symlink
    is_world_writable = RealIsWorldWritable().is_world_writable
