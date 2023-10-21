# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import os
import sys

import trashcli.trash
from .file_system import RealRestoreReadFileSystem, \
    RealRestoreWriteFileSystem, RealReadCwd, RealFileReader, \
    RealListingFileSystem
from .info_dir_searcher import InfoDirSearcher
from .info_files import InfoFiles
from .restore_cmd import RestoreCmd
from .trash_directories import TrashDirectoriesImpl
from .trashed_files import TrashedFiles
from ..fstab.volumes import RealVolumes
from ..lib.logger import my_logger
from ..lib.my_input import RealInput


def main():
    info_files = InfoFiles(RealListingFileSystem())
    volumes = RealVolumes()
    trash_directories = TrashDirectoriesImpl(volumes,
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
        input=RealInput(),
        version=trashcli.trash.version,
        trashed_files=trashed_files,
        read_fs=RealRestoreReadFileSystem(),
        write_fs=RealRestoreWriteFileSystem(),
        read_cwd=RealReadCwd()
    ).run(sys.argv)
