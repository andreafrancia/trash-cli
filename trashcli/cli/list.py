#!/usr/bin/python
# trash-list: list trashed files
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

from trashcli.trash import GlobalTrashCan 
import sys

class List:
    def __init__(self, out):
        self.out = out
    def main(self, *argv):
        program_name=argv[0]
        import getopt
        options, arguments = getopt.gnu_getopt(argv, '', ('help'))
    
        for option, value in options:
            if option == '--help':
                self.out.write("""\
Usage: %s

List trashed files

Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit

Report bugs to http://code.google.com/p/trash-cli/issues
""" % program_name)
            return

        trashsystem = GlobalTrashCan()
        for trashed_file in trashsystem.trashed_files() :
            print "%s %s" % (trashed_file.deletion_date, trashed_file.path)

def main():
    List(sys.stdout).main(sys.argv)
