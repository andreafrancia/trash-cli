# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys
from typing import Mapping, TextIO, List

import trashcli.trash
from trashcli.empty.main import ContentReader
from trashcli.compat import Protocol
from trashcli.fslib.file_system_reader import FileSystemReader
from trashcli.fslib.protocols.file_size import FileSize
from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.fslib.real.real_fs import RealFs
from trashcli.fslib.real.real_read_file import RealReadFile
from trashcli.fslib.real.real_volume_of import RealVolumeOfFs
from trashcli.fslib.real.real_volumes_listing import RealVolumesListing
from trashcli.fstab.protocols.df_command import DfCommand
from trashcli.fstab.protocols.disk_partitions_fs import DiskPartitionsFs
from trashcli.fstab.real.real_df_command import RealDfCommand
from trashcli.fstab.real.real_disk_partitions_fs import RealDiskPartitionsFs
from trashcli.fslib.protocols.volume_of import VolumeOfFs
from trashcli.fslib.protocols.dir_reader_fs import DirReaderFs
from trashcli.fslib.real.real_dir_reader_fs import RealDirReaderFs
from trashcli.lib.print_version import PrintVersionArgs, \
    PrintVersionAction
from trashcli.list.list_trash_action import ListTrashAction, ListTrashArgs
from trashcli.list.minor_actions.debug_volumes import DebugVolumes, \
    DebugVolumesArgs
from trashcli.list.minor_actions.list_trash_dirs import ListTrashDirs, \
    ListTrashDirsArgs
from trashcli.list.minor_actions.list_volumes import PrintVolumesList, \
    PrintVolumesArgs
from trashcli.list.minor_actions.print_python_executable import \
    PrintPythonExecutable, PrintPythonExecutableArgs
from trashcli.list.parser import Parser
from trashcli.list.trash_dir_selector import TrashDirsSelector
from trashcli.trash_dirs_scanner import TopTrashDirRulesFs


class ListFileReader(TopTrashDirRulesFs, FileSize, Protocol):
    pass


def main():
    ListCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
        volumes_listing=RealVolumesListing(),
        uid=os.getuid(),
        volumes=RealVolumeOfFs(),
        dir_reader=RealDirReaderFs(RealFs()),
        file_reader=FileSystemReader(RealFs()),
        content_reader=RealReadFile(),
        version=trashcli.trash.version,
        disk_partitions_fs=RealDiskPartitionsFs(),
        df_command=RealDfCommand(),
    ).run(sys.argv)


class ListCmd:
    def __init__(self,
                 out,  # type: TextIO
                 err,  # type: TextIO
                 environ,  # type: Mapping[str, str]
                 volumes_listing,  # type: VolumesListing
                 uid,  # type: int
                 volumes,  # type: VolumeOfFs
                 file_reader,  # type: ListFileReader
                 dir_reader,  # type: DirReaderFs
                 content_reader,  # type: ContentReader
                 version,  # type: str
                 disk_partitions_fs,  # type: DiskPartitionsFs
                 df_command,  # type: DfCommand
                 ):
        self.out = out
        self.err = err
        self.version = version
        self.dir_reader = dir_reader
        self.content_reader = content_reader
        self.environ = environ
        self.uid = uid
        self.volumes_listing = volumes_listing
        self.selector = TrashDirsSelector.make(volumes_listing,
                                               file_reader,
                                               volumes)
        self.actions = {PrintVersionArgs: PrintVersionAction(self.out,
                                                             self.version),
                        PrintVolumesArgs: PrintVolumesList(self.environ,
                                                           self.volumes_listing,
                                                           self.out),
                        DebugVolumesArgs: DebugVolumes(self.out,
                                                       disk_partitions_fs,
                                                       df_command),
                        ListTrashDirsArgs: ListTrashDirs(self.environ,
                                                         self.uid,
                                                         self.selector,
                                                         self.out),
                        ListTrashArgs: ListTrashAction(self.environ,
                                                       self.uid,
                                                       self.selector,
                                                       self.out,
                                                       self.err,
                                                       self.dir_reader,
                                                       self.content_reader,
                                                       file_reader),
                        PrintPythonExecutableArgs: PrintPythonExecutable(
                            self.out)}

    def run(self,
            argv,  # type: List[str]
            ):  # type: (...) -> None
        parser = Parser(os.path.basename(argv[0]))
        args = parser.parse_list_args(argv[1:], argv[0])

        action = self.actions[type(args)]

        action.run_action(args)
