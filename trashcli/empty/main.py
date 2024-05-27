# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from datetime import datetime

from trashcli import trash
from trashcli.compat import Protocol
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.fs import FileReader
from .existing_file_remover import ExistingFileRemover
from .file_system_dir_reader import FileSystemDirReader
from .top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirRulesReader
from ..fs_impl import RealFileReader
from ..fstab.mount_points_listing import RealMountPointsListing
from ..fstab.real_volume_of import RealVolumeOf


def main():
    empty_cmd = EmptyCmd(argv0=sys.argv[0],
                         out=sys.stdout,
                         err=sys.stderr,
                         now=datetime.now,
                         file_reader=RealTopTrashDirRulesReader(),
                         file_remover=ExistingFileRemover(),
                         content_reader=FileSystemContentReader(),
                         dir_reader=FileSystemDirReader(),
                         version=trash.version,
                         volumes=RealVolumeOf(),
                         mount_point_listing=RealMountPointsListing()
                         )
    return empty_cmd.run_cmd(sys.argv[1:], os.environ, os.getuid())


class ContentReader(FileReader, Protocol):
    pass


class FileSystemContentReader(ContentReader, RealFileReader):
    pass
