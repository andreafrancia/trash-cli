# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys

import trashcli.trash
from trashcli.empty.main import ContentReader
from trashcli.file_system_reader import FileSystemReader
from trashcli.fs import RealContentsOf
from trashcli.fstab.volume_listing import RealVolumesListing
from trashcli.fstab.volume_of import RealVolumeOf
from trashcli.fstab.volume_of import VolumeOf
from trashcli.lib.dir_reader import DirReader, RealDirReader
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
from trashcli.trash_dirs_scanner import TopTrashDirRules


def main():
    ListCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
        volumes_listing=RealVolumesListing(),
        uid=os.getuid(),
        volumes=RealVolumeOf(),
        dir_reader=RealDirReader(),
        file_reader=FileSystemReader(),
        content_reader=RealContentsOf(),
        version=trashcli.trash.version
    ).run(sys.argv)


class ListCmd:
    def __init__(self,
                 out,
                 err,
                 environ,
                 volumes_listing,
                 uid,
                 volumes,  # type: VolumeOf
                 file_reader, # type: TopTrashDirRules.Reader
                 dir_reader,  # type: DirReader
                 content_reader, # type: ContentReader
                 version,
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
                                                           self.volumes_listing),
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
