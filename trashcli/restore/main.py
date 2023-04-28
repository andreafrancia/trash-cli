# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import sys

import trashcli.trash
from ..lib.logger import my_logger
from .file_system import RestoreFileSystem
from .restore_cmd import RestoreCmd
from .trash_directories import make_trash_directories, TrashDirectory
from .trashed_file import TrashedFiles
from ..fs import contents_of
from ..lib.my_input import my_input
from ..list_mount_points import os_mount_points


def main():
    trash_directories = make_trash_directories()
    trashed_files = TrashedFiles(my_logger,
                                 trash_directories,
                                 TrashDirectory(),
                                 contents_of)
    RestoreCmd.make(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        input=my_input,
        version=trashcli.trash.version,
        trashed_files=trashed_files,
        mount_points=os_mount_points,
        fs=RestoreFileSystem()
    ).run(sys.argv)
