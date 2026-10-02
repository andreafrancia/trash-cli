from trashcli.compat import Protocol
from trashcli.fstab.protocols.mount_point_list_fs import MountPointListFs
from trashcli.fstab.volume_of import VolumeOf


class Volumes(VolumeOf, MountPointListFs, Protocol):
    pass
