from trashcli.fslib.real.real_list_files_in_dir import RealListFilesInDir
from trashcli.fstab.volumes import RealVolumes
from trashcli.restore.fs.protocols.restore_read_fs import RestoreReadFs
from trashcli.restore.fs.real.real_file_reader_fs import RealFileReaderFs
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_read_cwd_fs import RealReadCwdFs


class RealRestoreReadFs(RestoreReadFs,
                        RealListFilesInDir,
                        RealFileReaderFs,
                        RealPathReaderFs,
                        RealVolumes,
                        RealReadCwdFs,
                        ):
    pass
