from trashcli.fslib.protocols.volumes_listing import VolumesListing


class NoVolumesListing(VolumesListing):
    def list_volumes(self, environ):
        return []
