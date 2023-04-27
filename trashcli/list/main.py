# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os
import sys

from trashcli import fstab
from trashcli.fstab import VolumesListing
from trashcli.list.list_cmd import ListCmd
from trashcli.list_mount_points import os_mount_points


def main():
    ListCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
        uid=os.getuid(),
        volumes_listing=VolumesListing(os_mount_points),
        volumes=fstab.volumes
    ).run(sys.argv)


def description(program_name, printer):
    printer.usage('Usage: %s [OPTIONS...]' % program_name)
    printer.summary('List trashed files')
    printer.options(
        "  --version   show program's version number and exit",
        "  -h, --help  show this help message and exit")
    printer.bug_reporting()
