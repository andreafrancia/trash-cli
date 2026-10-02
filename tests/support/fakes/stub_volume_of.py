from trashcli.fslib.protocols.volume_of import VolumeOfFs


class StubVolumeOfFs(VolumeOfFs):
    def volume_of(self, path):
        return "volume_of %s" % path
