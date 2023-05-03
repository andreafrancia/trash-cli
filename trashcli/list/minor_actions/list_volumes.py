class PrintVolumesArgs:
    pass


class PrintVolumesList:
    def __init__(self, environ, volumes_listing):
        self.environ = environ
        self.volumes_listing = volumes_listing

    def exectute(self,
                 args, # type: PrintVolumesArgs
                 ):
        for volume in self.volumes_listing.list_volumes(self.environ):
            print(volume)
