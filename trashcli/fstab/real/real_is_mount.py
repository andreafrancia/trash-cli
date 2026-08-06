import os

from trashcli.fstab.is_mount import IsMount


class RealIsMount(IsMount):
    def is_mount(self, path):
        return os.path.ismount(path)
