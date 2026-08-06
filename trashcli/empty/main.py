# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from datetime import datetime

from trashcli.compat import Protocol

from trashcli import trash
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.fslib.fs_operations import ContentsOf
from trashcli.fslib.real_fs_operations import RealContentsOf
from .existing_file_remover import ExistingFileRemover
from .file_system_dir_reader import FileSystemDirReader
from .top_trash_dir_rules_file_system_reader import \
    RealTopTrashDirFs
from trashcli.fstab.real.real_list_volume_fs import RealListVolumeFs
from ..fstab.real.real_volumes import RealVolumes


class ContentReader(ContentsOf, Protocol):
    pass


def main():
    empty_cmd = EmptyCmd(argv0=sys.argv[0],
                         out=sys.stdout,
                         err=sys.stderr,
                         volumes_listing=RealListVolumeFs(),
                         now=datetime.now,
                         file_reader=RealTopTrashDirFs(),
                         file_remover=ExistingFileRemover(),
                         content_reader=FileSystemContentReader(),
                         dir_reader=FileSystemDirReader(),
                         version=trash.version,
                         volumes=RealVolumes())
    return empty_cmd.run_cmd(sys.argv[1:], os.environ, os.getuid())


class FileSystemContentReader(ContentReader, RealContentsOf):
    pass
