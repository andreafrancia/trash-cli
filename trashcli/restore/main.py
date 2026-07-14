# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from .real_restore_fs import RealPathReaderFs, \
    RealRestoreWriterFs, RealReadCwdFs, RealFileReaderFs
from .real_restore_logger import RealRestoreLogger
from .restore_cmd import RestoreCmd
from ..empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from ..fslib.real_fs_operations import RealListFilesInDir
from ..fstab.volumes import RealVolumes
from ..lib.logger import my_logger
from ..lib.my_input import RealInput


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
        read_cwd=RealReadCwdFs()
    ).run(sys.argv)
