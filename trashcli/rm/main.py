# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
from typing import Callable, Mapping
import sys

from trashcli.fslib.real.real_entries_if_dir_exists import \
    RealEntriesIfDirExists
from trashcli.fslib.protocols.fs import Fs
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_is_sym_link import RealIsSymLink
from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.fslib.real.real_volumes_listing import RealVolumesListing
from trashcli.rm.real_remover_fs import RealRemoverFs
from trashcli.rm.rm_cmd import RmCmd, RmFileSystemReader


def main():
    volumes_listing = RealVolumesListing()
    cmd = RmCmd(environ=os.environ,
                getuid=os.getuid,
                volumes_listing=volumes_listing,
                stderr=sys.stderr,
                file_reader=RealRmFileSystemReader(RealFs(), os.environ,
                                                   os.geteuid))

    cmd.run(sys.argv, os.getuid())

    return cmd.exit_code


class RealRmFileSystemReader(RmFileSystemReader):
    def __init__(self,
                 fs,  # type: Fs
                 environ,  # type: Mapping[str, str]
                 geteuid,  # type: Callable[[], int]
                 ):  # type: (...) -> None
        self.fs = fs
        self.environ = environ
        self.geteuid = geteuid

    def read_file(self, path):
        return RealReadFile().read_file(path)

    def is_symlink(self, path):  # type: (str) -> bool
        return RealIsSymLink().is_symlink(path)

    def is_sticky_dir(self, path):  # type: (str) -> bool
        return self.fs.is_sticky_dir(path)

    def is_world_writable(self, path):  # type: (str) -> bool
        return self.fs.is_world_writable(path)

    def entries_if_dir_exists(self, path):
        return RealEntriesIfDirExists(self.fs).entries_if_dir_exists(path)

    def path_exists(self, path):
        return self.fs.path_exists(path)

    def path_isdir(self, path):  # type: (str) -> bool
        return self.fs.path_isdir(path)

    def remove_file2(self, path):
        return RealRemoverFs(self.fs, self.environ, self.geteuid).remove_file2(
            path)

    def remove_file_if_exists(self, path):
        return RealRemoverFs(self.fs, self.environ,
                             self.geteuid).remove_file_if_exists(path)
