#!/usr/bin/env python
# setup.py: Python distutils script
#
# Copyright (C) 2007,2008 Andrea Francia Trivolzio(PV) Italy
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

"""Installation script for trash-cli.
Run it with
 './setup.py install', or
 './setup.py --help' for more options
"""

from distutils.core import setup
import sys
import os
sys.path.append('src')

import libtrash 



setup_args = {
    'name':         'trash-cli',
    'version':      libtrash.version,
    'author':       'Andrea Francia',
    'author_email': 'andreafrancia@users.sourceforge.net',
    'url':          'http://code.google.com/p/trash-cli',
    'description':  'Command line interface to FreeDesktop.org Trash.',
    'license':      'GPL v2',
    'download_url': 'http://code.google.com/p/trash-cli/wiki/Download',
    'long_description': 
"""trash-cli - Command Line Interface to FreeDesktop.org Trash.

trash-cli provides the following commands to manage the trash:

* trash                 trashes files and directories.
* empty-trash           empty the trashcan(s).
* list-trash            list trashed file.
* restore-trash         restore a trashed file.
* trash-admin           administrate trashcan(s).

For each file the name, original path, deletion date, and permissions
are recorded. The trash command allow trash multiple files with the
same name. These command uses the same Trashcan of last versions of
KDE, GNOME and XFCE.

Trash a file:
$ trash /home/andrea/foobar

List trashed files:
$ list-trash
2008-06-01 10:30:48 /home/andrea/bar
2008-06-02 21:50:41 /home/andrea/bar
2008-06-23 21:50:49 /home/andrea/foo

Restore a trashed file:
$ restore-trash /home/andrea/foo

Empty the trashcan:
$ empty-trash""",
    'packages' : ['libtrash'],
    'scripts'  : ['src/trash-file',
                  'src/trash-list',
                  'src/trash-restore',
                  'src/trash-empty'],
    'package_dir' : {'':'src'},
    'data_files': [('man/man1', ['man/man1/trash-empty.1',
                                 'man/man1/trash-list.1',
                                 'man/man1/trash-restore.1',
                                 'man/man1/trash-file.1'])]

    }


setup(**setup_args)
