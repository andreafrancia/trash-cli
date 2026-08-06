from trashcli.compat import Protocol
from trashcli.fstab.is_mount import IsMount
from trashcli.fstab.list_volume_fs import ListVolumeFs
from trashcli.fstab.volume_of import VolumeOf


class Volumes(IsMount,
              VolumeOf,
              ListVolumeFs,
              Protocol):
    pass
