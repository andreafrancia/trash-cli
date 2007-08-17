#!/usr/bin/python

from distutils.core import setup

setup(name='trash',
      description='Command line interface to trash '
                  + '(compatible with Trash Spec from FreeDesktop.org',
      author='Andrea Francia',
      author_email='andrea.francia@users.sourceforge.net',
      url='bluetrash.sourceforge.net',
      version='0.1.2',
      py_modules=['libtrash'],
      scripts=['trash', 'list-trash', 'restore-trash']
      )
