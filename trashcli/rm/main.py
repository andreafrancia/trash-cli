# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
import sys

from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_volumes_listing import RealVolumesListing
from trashcli.rm.rm_cmd import RmCmd
from trashcli.rm.rm_fs_impl import RmFsImpl


def main():
    volumes_listing = RealVolumesListing()
    cmd = RmCmd(environ=os.environ,
                getuid=os.getuid,
                volumes_listing=volumes_listing,
                stderr=sys.stderr,
                rm_fs=RmFsImpl(RealFs(), os.environ,
                               os.geteuid))

    cmd.run(sys.argv, os.getuid())

    return cmd.exit_code
