#!/usr/bin/python

from distutils.core import setup

import libtrash

DOC_FILES = ('COPYING', 'INSTALL', 'README', 'AUTHORS')

setup(name='trash',
      description='Command line trashcan (recycle bin) interface',
      author='Andrea Francia',
      author_email='andreafrancia@users.sourceforge.net',
      url='http://bluetrash.sourceforge.net/',
      version=libtrash.version,
      py_modules=['libtrash'],
      scripts=['trash', 'list-trash', 'restore-trash', 'empty-trash'],
      license='GPL',
      long_description='Command line interface to trash '
                     + 'compatible with Trash Spec from FreeDesktop.org',
      data_files = [ (".", DOC_FILES) ], 
      )
