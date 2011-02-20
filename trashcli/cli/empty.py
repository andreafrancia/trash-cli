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

from trashcli.trash import GlobalTrashCan

def main() :
    import sys
    from datetime import datetime
    TrashEmptyCommand(GlobalTrashCan(), datetime.now).run_with_argv(sys.argv) 

class TrashEmptyCommand:
    from datetime import datetime 
    def __init__(self,trashcan,now):
        self.trashcan = trashcan
        self.now = now

    def run_with_argv(self,argv):
        """
        Empty the trash. If a command line parameter is given we delete only files
        older than that parameter (integer, days).
        """

        parser = get_option_parser()
        (options, args) = parser.parse_args(argv[1:])

        if len(args) > 1 :
            parser.print_usage()
            parser.exit()
        elif len(args) == 1 :
            try :
                days=int(args[0])
                self.delete_file_trashed_more_than_N_days_ago(days)
            except ValueError:
                parser.print_usage()
                parser.exit()
        else:
             self.delete_all_files()

    def delete_all_files(self):
        for trashedfile in self.trashcan.trashed_files():
            self.trashcan.purge(trashedfile)

    def delete_file_trashed_more_than_N_days_ago(self, days):
        for trashedfile in self.trashcan.trashed_files() :
            delta=self.now()-trashedfile.deletion_date
            if delta.days >= days :
                self.trashcan.purge(trashedfile)

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

# eof
