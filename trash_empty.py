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

import sys
import os

from trashcli.trash2 import EmptyCmd

def main():
    EmptyCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
    ).run(*sys.argv)
    print 'ciao'
    print sys.argv
    sys.stdout.write('ciao')

if __name__ == '__main__':
    main()
