from pprint import pprint

from trashcli.lib.action import Action


class DebugVolumesArgs:
    pass


class DebugVolumes(Action):
    def run_action(self,
                   args,  # type: DebugVolumesArgs
                   ):
        import psutil
        import os
        all = sorted([p for p in psutil.disk_partitions(all=True)],
                     key=lambda p: p.device)
        physical = sorted([p for p in psutil.disk_partitions()],
                          key=lambda p: p.device)
        virtual = [p for p in all if p not in physical]
        print("physical ->")
        pprint(physical)
        print("virtual ->")
        pprint(virtual)
        os.system('df -P')
