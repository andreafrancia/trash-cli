# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys

import trashcli.trash
from trashcli.empty.main import ContentReader
from trashcli.file_system_reader import FileSystemReader
from trashcli.fs_impl import RealFileReader
from trashcli.fstab.mount_points_listing import MountPointsListing
from trashcli.fstab.mount_points_listing import RealMountPointsListing
from trashcli.fstab.real_volume_of import RealVolumeOf
from trashcli.fstab.volume_listing import VolumesListing
from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.dir_reader import DirReader
from trashcli.lib.dir_reader import RealDirReader
from trashcli.lib.print_version import PrintVersionAction
from trashcli.lib.print_version import PrintVersionArgs
from trashcli.list.list_trash_action import ListTrashAction
from trashcli.list.list_trash_action import ListTrashArgs
from trashcli.list.minor_actions.debug_volumes import DebugVolumes
from trashcli.list.minor_actions.debug_volumes import DebugVolumesArgs
from trashcli.list.minor_actions.list_trash_dirs import ListTrashDirs
from trashcli.list.minor_actions.list_trash_dirs import ListTrashDirsArgs
from trashcli.list.minor_actions.list_volumes import PrintVolumesArgs
from trashcli.list.minor_actions.list_volumes import PrintVolumesList
from trashcli.list.minor_actions.print_python_executable import \
    PrintPythonExecutable
from trashcli.list.minor_actions.print_python_executable import \
    PrintPythonExecutableArgs
from trashcli.list.parser import Parser
from trashcli.list.trash_dir_selector import TrashDirsSelector
from trashcli.trash_dirs_scanner import TopTrashDirRules


def main():
    ListCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
        uid=os.getuid(),
        volumes=RealVolumeOf(),
        dir_reader=RealDirReader(),
        file_reader=FileSystemReader(),
        content_reader=RealFileReader(),
        version=trashcli.trash.version,
        mount_points_listing=RealMountPointsListing(),
    ).run(sys.argv)


class ListCmd:
    def __init__(self,
                 out,
                 err,
                 environ,
                 uid,
                 volumes,  # type: VolumeOf
                 file_reader, # type: TopTrashDirRules.Reader
                 dir_reader,  # type: DirReader
                 content_reader, # type: ContentReader
                 version,
                 mount_points_listing,  # type: MountPointsListing
                 ):
        self.out = out
        self.err = err
        self.version = version
        self.dir_reader = dir_reader
        self.content_reader = content_reader
        self.environ = environ
        self.uid = uid
        self.selector = TrashDirsSelector.make(file_reader,
                                               volumes,
                                               mount_points_listing)
        self.actions = {PrintVersionArgs: PrintVersionAction(self.out,
                                                             self.version),
                        PrintVolumesArgs: PrintVolumesList(
                            self.environ, self.out, mount_points_listing),
                        DebugVolumesArgs: DebugVolumes(),
                        ListTrashDirsArgs: ListTrashDirs(self.environ,
                                                         self.uid,
                                                         self.selector),
                        ListTrashArgs: ListTrashAction(self.environ,
                                                       self.uid,
                                                       self.selector,
                                                       self.out,
                                                       self.err,
                                                       self.dir_reader,
                                                       self.content_reader),
                        PrintPythonExecutableArgs: PrintPythonExecutable()}

    def run(self, argv):
        parser = Parser(os.path.basename(argv[0]))
        args = parser.parse_list_args(argv[1:], argv[0])

        action = self.actions[type(args)]

        action.run_action(args)
