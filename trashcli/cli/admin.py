#!/usr/bin/python
# trashcan-admin: administer the trashcan
#
# Copyright (C) 2007-2009 Andrea Francia Trivolzio(PV) Italy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

def create_option_parser():
    """
    Creates and returns the option parser for the trash-admin command
    """
    import trashcli
    from optparse import OptionParser
    parser=OptionParser(usage="%prog [OPTION]... FILE...",
                        description="trashcan admin",
                        version="%%prog %s" % trashcli.version)

    parser.add_option("--volumes",
                      action="store_true",
                      help="List all volumes",
                      dest="volumes")

    parser.add_option("--trashcans",
                      action="store_true",
                      help="List all trashcan",
                      dest="trashcans")

    return parser


def main(argv=None) :
    from trashcli.filesystem import Volume

    parser = create_option_parser()
    (options, args) = parser.parse_args(argv)

    if options.volumes :
        for i in Volume.all() :
            print i.path
    elif options.trashcans :
        for i in trashcan.trash_directories() :
            print "%s (%s)" % (i, i.volume)