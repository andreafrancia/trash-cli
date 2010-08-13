#!/usr/bin/env python
# setup.py: Python distutils script
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

"""Installation script for trash-cli.
Run it with
 'python setup.py install', or
 'python setup.py --help' for more options
"""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup
from setuptools import find_packages
import sys
import os

try :
    sys.path.append("google-code")
    from googlecode_distutils_upload import upload as google_upload
except ImportError:
    from distutils.core import Command
    class google_upload(Command):
        user_options = []
        def __init__(self, *args, **kwargs):
            sys.stderr.write("""\
error: Install this module in site-packages to upload:
http://support.googlecode.com/svn/trunk/scripts/googlecode_distutils_upload.py
""")
            sys.exit(3)

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
    install_requires="Unipath>=0.2.0",
    author = 'Andrea Francia',
    author_email = 'andreafrancia@users.sourceforge.net',
    url = 'http://code.google.com/p/trash-cli',
    description = 'Command line interface to FreeDesktop.org Trash.',
    license = 'GPL v2',
    download_url = 'http://code.google.com/p/trash-cli/wiki/Download',
    long_description = read_description(),
    packages = find_packages(exclude=["tests", "tests.*"]),
    test_suite = "nose.collector",
    entry_points = {
        'console_scripts' : [
            'trash-list = trashcli.cli.list:main',
            'trash-put = trashcli.cli.put:main',
            'restore-trash = trashcli.cli.legacy_restore:main',
            'volume-of = trashcli.cli.volume_of:main',
            'trash-empty = trashcli.cli.empty:main'
        ]
    },
    data_files = [('man/man1', ['man/man1/trash-empty.1',
                                'man/man1/trash-list.1',
                                'man/man1/trash-restore.1',
                                'man/man1/trash-put.1'])],
    cmdclass={'google_upload': google_upload},
    )

