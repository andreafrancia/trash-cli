# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from datetime import datetime

from trashcli.compat import Protocol

from trashcli import trash
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.fs import RealContentsOf, ContentsOf
from .existing_file_remover import ExistingFileRemover
from .file_system_dir_reader import FileSystemDirReader
from .top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirRulesReader
from ..fstab.volume_listing import RealVolumesListing
from ..fstab.volume_of import RealVolumeOf


class ContentReader(ContentsOf, Protocol):
    pass


def main():
    empty_cmd = EmptyCmd(argv0=sys.argv[0],
                         out=sys.stdout,
                         err=sys.stderr,
                         volumes_listing=RealVolumesListing(),
                         now=datetime.now,
                         file_reader=RealTopTrashDirRulesReader(),
                         file_remover=ExistingFileRemover(),
                         content_reader=FileSystemContentReader(),
                         dir_reader=FileSystemDirReader(),
                         version=trash.version,
                         volumes=RealVolumeOf())
    return empty_cmd.run_cmd(sys.argv[1:], os.environ, os.getuid())


class FileSystemContentReader(ContentReader, RealContentsOf):
    pass
