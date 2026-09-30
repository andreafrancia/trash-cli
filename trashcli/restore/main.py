# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from trashcli.restore.fs.real.real_path_reader_fs import RealPathReaderFs
from trashcli.restore.fs.real.real_restore_writer_fs import RealRestoreWriterFs
from trashcli.restore.fs.real.real_read_cwd_fs import RealReadCwdFs
from trashcli.restore.fs.real.real_file_reader_fs import RealFileReaderFs
from trashcli.restore.real_restore_logger import RealRestoreLogger
from trashcli.restore.restore_cmd import RestoreCmd
from trashcli.empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fslib.real.real_list_files_in_dir import RealListFilesInDir
from trashcli.fstab.volumes import RealVolumes
from trashcli.lib.logger import my_logger
from trashcli.lib.my_input import RealInput
from trashcli.put.fs.real_volume_path_fs import RealVolumePathFs


def main():
    RestoreCmd(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        input=RealInput(),
        version=trashcli.trash.version,
        listing_fs=RealListFilesInDir(),
        volumes=RealVolumes(),
        logger=RealRestoreLogger(my_logger),
        uid=os.getuid(),
        environ=os.environ,
        top_trash_dir_rules_fs=RealTopTrashDirFs(),
        file_reader=RealFileReaderFs(),
        read_fs=RealPathReaderFs(),
        write_fs=RealRestoreWriterFs(),
        read_cwd=RealReadCwdFs(),
        volume_path_fs=RealVolumePathFs(),
    ).run(sys.argv)
