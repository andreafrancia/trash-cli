from __future__ import print_function

from pprint import pformat
from typing import TextIO

from trashcli.fstab.protocols.df_command import DfCommand
from trashcli.fstab.protocols.disk_partitions_fs import DiskPartitionsFs
from trashcli.lib.action import Action


class DebugVolumesArgs:
    pass


class DebugVolumes(Action):
    def __init__(self,
                 out,  # type: TextIO
                 disk_partitions_fs,  # type: DiskPartitionsFs
                 df_command,  # type: DfCommand
                 ):
        self.out = out
        self.disk_partitions_fs = disk_partitions_fs
        self.df_command = df_command

    def run_action(self,
                   args,  # type: DebugVolumesArgs
                   ):
        all = sorted(self.disk_partitions_fs.disk_partitions(all=True),
                     key=lambda p: p.device)
        physical = sorted(self.disk_partitions_fs.disk_partitions(all=False),
                          key=lambda p: p.device)
        virtual = [p for p in all if p not in physical]
        print("physical ->", file=self.out)
        print(pformat(physical), file=self.out)
        print("virtual ->", file=self.out)
        print(pformat(virtual), file=self.out)
        self.out.write(self.df_command.df_output())
