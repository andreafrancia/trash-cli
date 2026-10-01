from trashcli.fslib.protocols.volumes_listing import VolumesListing


class FixedVolumesListing(VolumesListing):
    def __init__(self, volumes):
        self.volumes = volumes

    def list_volumes(self, _environ):
        return self.volumes
