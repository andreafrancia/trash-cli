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
from setuptools import find_packages
import sys
import os

sys.path.append("google-code")
from googlecode_distutils_upload import upload as google_upload

sys.path.append('.')
import trashcli 

def read_description():
    f = open("description.txt")
    try :
        return f.read()
    finally:
        f.close()

setup(
    name = 'trash-cli',
    version = trashcli.version,
    author = 'Andrea Francia',
    author_email = 'andreafrancia@users.sourceforge.net',
    url = 'http://code.google.com/p/trash-cli',
    description = 'Command line interface to FreeDesktop.org Trash.',
    license = 'GPL v2',
    download_url = 'http://code.google.com/p/trash-cli/wiki/Download',
    long_description = read_description(),
    packages = ['trashcli', 'trashcli.cli'],
    scripts = ['scripts/trash-file',
               'scripts/trash-list',
               'scripts/volume-of',
               'scripts/restore-trash',
               # 'scripts/trash-restore',  # not ready yet
               'scripts/trash-restore',
               'scripts/trash-empty'],
    data_files = [('man/man1', ['man/man1/trash-empty.1',
                                'man/man1/trash-list.1',
                                'man/man1/trash-restore.1',
                                'man/man1/trash-file.1'])],
    cmdclass={'google_upload': google_upload},
    )

