# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys

import trashcli.trash
from trashcli.fslib.real.real_dir_reader_fs import RealDirReaderFs
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_volume_of import RealVolumeOfFs
from trashcli.fslib.real.real_volumes_listing import RealVolumesListing
from trashcli.fstab.real.real_df_command import RealDfCommand
from trashcli.fstab.real.real_disk_partitions_fs import RealDiskPartitionsFs
from trashcli.list.list_cmd import ListCmd
from trashcli.list.list_fs_impl import ListFsImpl


def main():
    fs = RealFs()
    ListCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
        volumes_listing=RealVolumesListing(),
        uid=os.getuid(),
        volumes=RealVolumeOfFs(),
        dir_reader=RealDirReaderFs(fs),
        file_reader=ListFsImpl(fs),
        content_reader=fs,
        version=trashcli.trash.version,
        disk_partitions_fs=RealDiskPartitionsFs(),
        df_command=RealDfCommand(),
    ).run(sys.argv)
