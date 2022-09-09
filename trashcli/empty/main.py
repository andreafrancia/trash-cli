# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from datetime import datetime

from trashcli import trash
from trashcli.fs import FileRemover, FileSystemContentReader, \
    FileSystemDirReader, TopTrashDirRulesFileSystemReader
from trashcli.list_mount_points import os_mount_points
from trashcli.empty.empty_cmd import EmptyCmd
from ..fstab import volume_of, VolumesListing
from .. import fstab


def main():
    empty_cmd = EmptyCmd(argv0=sys.argv[0], out=sys.stdout, err=sys.stderr,
                         environ=os.environ,
                         volumes_listing=VolumesListing(os_mount_points),
                         now=datetime.now,
                         file_reader=TopTrashDirRulesFileSystemReader(),
                         getuid=os.getuid, file_remover=FileRemover(),
                         content_reader=FileSystemContentReader(),
                         dir_reader=FileSystemDirReader(),
                         version=trash.version, volumes=fstab.volumes)
    return empty_cmd.run(sys.argv[1:], os.environ)
