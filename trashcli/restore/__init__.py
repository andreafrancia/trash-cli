import sys

from .file_system import RestoreFileSystem
from .restore_cmd import RestoreCmd
from .trash_directories import make_trash_directories, TrashDirectory
from .trashed_file import TrashedFiles
from .. import trash
from ..fs import contents_of
from ..lib.my_input import my_input
from ..list_mount_points import os_mount_points
from .range import Range
from .sequences import Sequences
from .single import Single
from .my_range import my_range


def main():
    trash_directories = make_trash_directories()
    logger = trash.logger
    trashed_files = TrashedFiles(logger,
                                 trash_directories,
                                 TrashDirectory(),
                                 contents_of)
    RestoreCmd(
        stdout=sys.stdout,
        stderr=sys.stderr,
        exit=sys.exit,
        input=my_input,
        trashed_files=trashed_files,
        mount_points=os_mount_points,
        fs=RestoreFileSystem()
    ).run(sys.argv)
