# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys

import trashcli.trash
from trashcli import fstab
from trashcli.file_system_reader import FileSystemReader
from trashcli.fstab import VolumesListing, Volumes
from trashcli.list.actions import Action
from trashcli.list.list_trash_action import ListTrashAction
from trashcli.list.minor_actions.debug_volumes import DebugVolumes
from trashcli.list.minor_actions.list_trash_dirs import ListTrashDirs
from trashcli.list.minor_actions.list_volumes import PrintVolumesList
from trashcli.list.minor_actions.print_python_executable import \
    PrintPythonExecutable
from trashcli.list.minor_actions.print_version import PrintVersion
from trashcli.list.parser import Parser
from trashcli.list.trash_dir_selector import TrashDirsSelector
from trashcli.list_mount_points import os_mount_points


def main():
    ListCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
        volumes_listing=VolumesListing(os_mount_points),
        uid=os.getuid(),
        volumes=fstab.volumes,
        file_reader=FileSystemReader(),
        version=trashcli.trash.version
    ).run(sys.argv)


class ListCmd:
    def __init__(self,
                 out,
                 err,
                 environ,
                 volumes_listing,
                 uid,
                 volumes,  # type: Volumes
                 file_reader,
                 version,
                 ):
        self.out = out
        self.err = err
        self.version = version
        self.file_reader = file_reader
        self.environ = environ
        self.uid = uid
        self.volumes_listing = volumes_listing
        self.selector = TrashDirsSelector.make(volumes_listing,
                                               file_reader,
                                               volumes)

    def run(self, argv):
        parser = Parser(os.path.basename(argv[0]))
        parsed = parser.parse_list_args(argv[1:])
        actions = {}
        actions[Action.print_version] = PrintVersion(self.out, argv[0],
                                                     self.version)
        actions[Action.list_volumes] = PrintVolumesList(self.environ,
                                                        self.volumes_listing)
        actions[Action.debug_volumes] = DebugVolumes()
        actions[Action.list_trash_dirs] = ListTrashDirs(self.environ,
                                                        self.uid,
                                                        self.selector)
        actions[Action.list_trash] = ListTrashAction(self.environ,
                                                     self.uid,
                                                     self.selector,
                                                     self.out,
                                                     self.err,
                                                     self.file_reader)
        actions[Action.print_python_executable] = PrintPythonExecutable()

        action = actions.get(parsed.action)

        action.execute(parsed)
