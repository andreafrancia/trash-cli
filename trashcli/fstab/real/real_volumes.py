from trashcli.fstab.real.real_is_mount import RealIsMount
from trashcli.fstab.real.real_list_volume_fs import RealListVolumeFs
from trashcli.fstab.real.real_volume_of import RealVolumeOf
from trashcli.fstab.volumes import Volumes


class RealVolumes(RealIsMount,
                  RealVolumeOf,
                  RealListVolumeFs,
                  Volumes):
    pass
