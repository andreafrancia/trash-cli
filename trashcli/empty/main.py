# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from datetime import datetime

from trashcli import trash
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.fs import (
    FileSystemContentReader,
    FileSystemDirReader,
    TopTrashDirRulesFileSystemReader,
)
from trashcli.list_mount_points import os_mount_points

from .. import fstab
from ..fstab import VolumesListing
from .existing_file_remover import ExistingFileRemover


def main():
    empty_cmd = EmptyCmd(argv0=sys.argv[0], out=sys.stdout, err=sys.stderr,
                         volumes_listing=VolumesListing(os_mount_points),
                         now=datetime.now,
                         file_reader=TopTrashDirRulesFileSystemReader(),
                         file_remover=ExistingFileRemover(),
                         content_reader=FileSystemContentReader(),
                         dir_reader=FileSystemDirReader(),
                         version=trash.version, volumes=fstab.volumes)
    return empty_cmd.run_cmd(sys.argv[1:], os.environ, os.getuid())
