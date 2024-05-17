from trashcli.fstab.volume_of import VolumeOf


class StubVolumeOf(VolumeOf):
    def volume_of(self, path):
        return "volume_of %s" % path
