class PrintVolumesList:
    def __init__(self, environ, volumes_listing):
        self.environ = environ
        self.volumes_listing = volumes_listing

    def exectute(self):
        for volume in self.volumes_listing.list_volumes(self.environ):
            print(volume)
