# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
import sys

from trashcli.fs_impl import RealFileReader
from trashcli.fs_impl import RealEntriesIfDirExists
from trashcli.fs_impl import RealPathExists
from trashcli.fs_impl import RealIsStickyDir
from trashcli.fs_impl import RealIsSymLink
from trashcli.fstab.mount_points_listing import RealMountPointsListing
from trashcli.rm.rm_cmd import RmCmd
from trashcli.rm.rm_cmd import RmFileSystemReader


def main():
    cmd = RmCmd(environ=os.environ,
                getuid=os.getuid,
                stderr=sys.stderr,
                file_reader=RealRmFileSystemReader(),
                mount_points_listing=RealMountPointsListing())

    cmd.run(sys.argv, os.getuid())

    return cmd.exit_code


class RealRmFileSystemReader(RmFileSystemReader,
                             RealPathExists,
                             RealIsStickyDir,
                             RealIsSymLink,
                             RealFileReader,
                             RealEntriesIfDirExists,
                             ):
    pass
