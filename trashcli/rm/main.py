# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
import sys

from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.real.real_exists import RealExists
from trashcli.fslib.real.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real.real_is_sym_link import RealIsSymLink
from trashcli.fslib.real.real_contents_of import RealContentsOf
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
