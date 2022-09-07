# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from datetime import datetime

from trashcli import trash
from trashcli.fs import FileRemover
from trashcli.fs import FileSystemReader
from trashcli.list_mount_points import os_mount_points
from trashcli.empty.empty_cmd import EmptyCmd
from ..fstab import volume_of, VolumesListing


def main():
    empty_cmd = EmptyCmd(out=sys.stdout, err=sys.stderr, environ=os.environ,
                         volumes_listing=VolumesListing(os_mount_points),
                         now=datetime.now, file_reader=FileSystemReader(),
                         getuid=os.getuid, file_remover=FileRemover(),
                         version=trash.version, volume_of=volume_of)
    return empty_cmd.run(sys.argv, os.environ)
