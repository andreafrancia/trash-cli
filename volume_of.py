# Copyright (C) 2007-20!! Andrea Francia Trivolzio(PV) Italy

import sys

def main(argv=sys.argv[1:]):
    from optparse import OptionParser
    from trashcli.trash import volume_of

    (options, args) = OptionParser().parse_args(argv)

    for arg in args :
        print '%s is in volume %s ' % (arg, volume_of(arg))
