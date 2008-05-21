#!/usr/bin/python

from distutils.core import setup

import libtrash 

setup(name='trash',
      description='Command line trashcan (recycle bin) interface',
      author='Andrea Francia',
      author_email='andreafrancia@users.sourceforge.net',
      url='http://bluetrash.sourceforge.net/',
      version=libtrash.version,
      py_modules=['libtrash', 'version'],
      scripts=['trash', 'list-trash', 'restore-trash', 'empty-trash'],
      license='GPL',
      long_description='Command line interface to trash '
                     + 'compatible with Trash Spec from FreeDesktop.org',
      )
