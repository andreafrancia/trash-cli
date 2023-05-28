# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
import sys

from trashcli.fs import RealExists, RealIsStickyDir, RealIsSymLink, \
    RealContentsOf, RealEntriesIfDirExists
from trashcli.fstab.volume_listing import RealVolumesListing
from trashcli.rm.rm_cmd import RmCmd, RmFileSystemReader


def main():
    volumes_listing = RealVolumesListing()
    cmd = RmCmd(environ=os.environ,
                getuid=os.getuid,
                volumes_listing=volumes_listing,
                stderr=sys.stderr,
                file_reader=RealRmFileSystemReader())

    cmd.run(sys.argv, os.getuid())

    return cmd.exit_code


class RealRmFileSystemReader(RmFileSystemReader,
                             RealExists,
                             RealIsStickyDir,
                             RealIsSymLink,
                             RealContentsOf,
                             RealEntriesIfDirExists,
                             ):
    pass
