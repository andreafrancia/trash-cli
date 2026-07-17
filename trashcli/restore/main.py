# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from .real_restore_fs import RealPathReaderFs, \
    RealRestoreWriterFs, RealReadCwdFs, RealFileReaderFs, RealRestoreReadFs
from .real_restore_logger import RealRestoreLogger
from .restore_cmd import RestoreCmd
from ..empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from ..fstab.volumes import RealVolumes
from ..lib.logger import my_logger
from ..lib.my_input import RealInput


def main():
    restore_read_fs = RealRestoreReadFs()
    RestoreCmd(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        input=RealInput(),
        version=trashcli.trash.version,
        volumes=RealVolumes(),
        logger=RealRestoreLogger(my_logger),
        uid=os.getuid(),
        environ=os.environ,
        write_fs=RealRestoreWriterFs(),

        listing_fs=restore_read_fs,
        top_trash_dir_rules_fs=RealTopTrashDirFs(),
        file_reader=RealFileReaderFs(),
        path_read_fs=RealPathReaderFs(),
        read_cwd=RealReadCwdFs()
    ).run(sys.argv)
