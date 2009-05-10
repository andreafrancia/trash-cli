#!/usr/bin/python
# trash-empty: remove file from trashcans
#
# Copyright (C) 2008 Einar Orn Olason
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

def get_option_parser():
    from trashcli import version
    from optparse import OptionParser
    from optparse import IndentedHelpFormatter
    from trashcli.cli.util import NoWrapFormatter

    parser = OptionParser(usage="%prog [days]",
                          description="Purge trashed files.",
                          version="%%prog %s" % version,
                          formatter=NoWrapFormatter(),
                          epilog=
    """Report bugs to http://code.google.com/p/trash-cli/issues""")

    return parser

def main(argv=None) :
    """
    Empty the trash. If a command line parameter is given we delete only files
    older than that parameter (integer, days).
    """
    # original author: Einar Orn Olason
    # modified by Andrea Francia (refactored, and OptionParser added)


    parser = get_option_parser()
    (options, args) = parser.parse_args(argv)

    import os, datetime, sys
    from trashcli.trash import trashcan

    days=0

    if len(args) > 1 :
        parser.print_usage()
        parser.exit()
    elif len(args) > 1 :
        try :
            days=int(args[1])
        except :
            parser.print_usage()

    for trashedfile in trashcan.trashed_files() :
        delta=datetime.datetime.now()-trashedfile.deletion_date
        if delta.days >= days :
            trashedfile.purge()

# eof
