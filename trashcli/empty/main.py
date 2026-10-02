# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from datetime import datetime

from trashcli.compat import Protocol

from trashcli import trash
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.fslib.protocols.read_file import ReadFile
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_volumes_listing import RealVolumesListing
from trashcli.fstab.real_volume_of import RealVolumeOf


class ContentReader(ReadFile, Protocol):
    pass


def main():
    empty_cmd = EmptyCmd(argv0=sys.argv[0],
                         out=sys.stdout,
                         err=sys.stderr,
                         volumes_listing=RealVolumesListing(),
                         now=datetime.now,
                         file_reader=RealFs(),
                         file_remover=ExistingFileRemover(RealFs()),
                         content_reader=RealFs(),
                         dir_reader=FileSystemDirReader(RealFs()),
                         version=trash.version,
                         volumes=RealVolumeOf())
    return empty_cmd.run_cmd(sys.argv[1:], os.environ, os.getuid())
