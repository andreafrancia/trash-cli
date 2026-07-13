# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from .file_system import RealRestoreReadFileSystem, \
    RealRestoreWriteFileSystem, RealReadCwd, RealFileReader, \
    RealListingFileSystem
from .real_restore_logger import RealRestoreLogger
from .restore_cmd import RestoreCmd
from ..empty.top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
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
        listing_file_system=RealListingFileSystem(),
        volumes=RealVolumes(),
        logger=RealRestoreLogger(my_logger),
        uid=os.getuid(),
        environ=os.environ,
        top_trash_dir_rules_fs=RealTopTrashDirFs(),
        file_reader=RealFileReader(),
        read_fs=RealRestoreReadFileSystem(),
        write_fs=RealRestoreWriteFileSystem(),
        read_cwd=RealReadCwd()
    ).run(sys.argv)
