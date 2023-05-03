# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from .file_system import RealRestoreReadFileSystem, \
    RealRestoreWriteFileSystem, RealReadCwd, RealFileReader, ListingFileSystem
from .info_dir_searcher import InfoDirSearcher
from .info_files import InfoFiles
from .restore_cmd import RestoreCmd
from .trash_directories import TrashDirectoriesImpl
from .trashed_file import TrashedFiles
from ..fstab.volumes import RealVolumes
from ..lib.logger import my_logger
from ..lib.my_input import my_input
from ..list_mount_points import RealMountPointsListing


def main():
    info_files = InfoFiles(ListingFileSystem())
    trash_directories = TrashDirectoriesImpl(RealMountPointsListing(),
                                             RealVolumes(),
                                             os.getuid(),
                                             os.environ)
    searcher = InfoDirSearcher(trash_directories, info_files)
    trashed_files = TrashedFiles(my_logger,
                                 RealFileReader(),
                                 searcher)
    RestoreCmd.make(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        input=my_input,
        version=trashcli.trash.version,
        trashed_files=trashed_files,
        read_fs=RealRestoreReadFileSystem(),
        write_fs=RealRestoreWriteFileSystem(),
        read_cwd=RealReadCwd()
    ).run(sys.argv)
