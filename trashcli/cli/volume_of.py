#!/usr/bin/python
# volume-of: determine the volume of a file
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

def get_option_parser():
    from optparse import OptionParser

    parser = OptionParser()
    return parser

def main(argv=None):
    from trashcli.filesystem import Path

    (options, args) = get_option_parser().parse_args(argv)

    for arg in args :
        print '%s is in volume %s ' % (Path(arg), Path(arg).volume)