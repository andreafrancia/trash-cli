from trashcli.fslib.protocols.volumes_listing import VolumesListing


class FakeVolumesListing(VolumesListing):
    def __init__(self, volumes=None):
        self.volumes = volumes if volumes is not None else []

    def list_volumes(self, environ):
        return self.volumes

    def add_volume(self, volume):
        self.volumes.append(volume)