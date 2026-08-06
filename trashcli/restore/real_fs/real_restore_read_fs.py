from trashcli.fslib.real_fs_operations import RealListFilesInDir
from trashcli.fstab.real.real_volumes import RealVolumes
from trashcli.restore.fs.restore_read_fs import RestoreReadFs
from trashcli.restore.real_fs.real_file_reader_fs import RealFileReaderFs
from trashcli.restore.real_fs.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.real_fs.real_read_cwd_fs import RealReadCwdFs


class RealRestoreReadFs(RestoreReadFs,
                        RealListFilesInDir,
                        RealFileReaderFs,
                        RealPathReaderFs,
                        RealVolumes,
                        RealReadCwdFs,
                        ):
    pass
