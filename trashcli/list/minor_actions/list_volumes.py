from __future__ import print_function


class PrintVolumesArgs(object):
    pass


class PrintVolumesList(object):
    def __init__(self, environ, volumes_listing, out):
        self.environ = environ
        self.volumes_listing = volumes_listing
        self.out = out

    def run_action(self,
                   args,  # type: PrintVolumesArgs
                   ):
        for volume in self.volumes_listing.list_volumes(self.environ):
            print(volume, file=self.out)
