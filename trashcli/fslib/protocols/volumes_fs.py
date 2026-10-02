from trashcli.compat import Protocol
from trashcli.fstab.protocols.mount_point_list_fs import MountPointListFs
from trashcli.fslib.protocols.volume_of import VolumeOfFs


class VolumesFs(VolumeOfFs, MountPointListFs, Protocol):
    pass
