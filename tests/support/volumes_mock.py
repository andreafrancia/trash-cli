from mock import Mock

from trashcli.fstab import Volumes


def volumes_mock(func = lambda x: "volume_of %s" % x):
    volumes = Mock(spec=Volumes)
    volumes.volume_of = func
    return volumes
