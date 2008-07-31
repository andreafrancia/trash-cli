#!/usr/bin/python
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

from distutils.core import setup
import sys
sys.path.append('src')

import libtrash 

setup(name='trash',
      description='Command line trashcan (recycle bin) interface',
      author='Andrea Francia',
      author_email='andreafrancia@users.sourceforge.net',
      url='http://bluetrash.sourceforge.net/',
      version=libtrash.version,
      packages=['libtrash'],
      scripts=['src/trash', 
	       'src/list-trash', 
	       'src/restore-trash', 
	       'src/empty-trash'],
      license='GPL',
      package_dir={'':'src'},
      long_description='Command line interface to trash '
                     + 'compatible with Trash Spec from FreeDesktop.org',
      )
