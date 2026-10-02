# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
import sys

from trashcli.fslib.real.real_entries_if_dir_exists import RealEntriesIfDirExists
from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_exists import RealExists
from trashcli.fslib.real.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real.real_is_sym_link import RealIsSymLink
from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.fslib.real.real_volumes_listing import RealVolumesListing
from trashcli.fslib.real.real_is_world_writable import RealIsWorldWritable
from trashcli.fslib.real.real_path_is_dir import RealPathIsDir
from trashcli.rm.real_remover_fs import RealRemoverFs
from trashcli.rm.rm_cmd import RmCmd, RmFileSystemReader


def main():
    volumes_listing = RealVolumesListing()
    cmd = RmCmd(environ=os.environ,
                getuid=os.getuid,
                volumes_listing=volumes_listing,
                stderr=sys.stderr,
                file_reader=RealRmFileSystemReader(RealFs()))

    cmd.run(sys.argv, os.getuid())

    return cmd.exit_code


class RealRmFileSystemReader(RmFileSystemReader,
                             RealExists,
                             RealIsStickyDir,
                             RealIsSymLink,
                             RealIsWorldWritable,
                             RealReadFile,
                             RealEntriesIfDirExists,
                             RealPathIsDir,
                             RealRemoverFs,
                             ):
    def __init__(self, fs):  # type: (Fs) -> None
        RealRemoverFs.__init__(self, fs)
