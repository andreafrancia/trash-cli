from __future__ import print_function

from typing import Mapping

from trashcli.fslib.protocols.volumes_listing import VolumesListing
from trashcli.lib.action import Action


class PrintVolumesArgs(object):
    pass


class PrintVolumesList(Action):
    def __init__(self,
                 environ,  # type: Mapping[str, str]
                 volumes_listing,  # type: VolumesListing
                 out,
                 ):
        self.environ = environ
        self.volumes_listing = volumes_listing
        self.out = out

    def run_action(self,
                   args,  # type: PrintVolumesArgs
                   ):
        for volume in self.volumes_listing.list_volumes(self.environ):
            print(volume, file=self.out)
