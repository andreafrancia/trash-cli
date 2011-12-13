#!/usr/bin/env python
# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy
# Distributed under the GPLv2 license (see the COPYING file).
# Distributed without any warranty.

import ez_setup; ez_setup.use_setuptools()
from setuptools import setup
from setuptools import find_packages

import sys
sys.path.append('.')
import trashcli

setup(
    name = 'trash-cli',
    version = trashcli.version,
    author = 'Andrea Francia',
    author_email = 'me@andreafrancia.it',
    url = 'https://github.com/andreafrancia/trash-cli',
    description = 'Command line interface to FreeDesktop.org Trash.',
    license = 'GPL v2',
    long_description = file("README.txt").read(),
    packages = find_packages(exclude=["tests", "tests.*"]),
    test_suite = "nose.collector",
    entry_points = {
        'console_scripts' : [
            'trash-list    = trash_list:main',
            'trash-put     = trash_put:main',
            'restore-trash = restore_trash:main',
            'volume-of     = volume_of:main',
            'trash-empty   = trash_empty:main'
        ]
    },
    data_files = [('man/man1', ['man/man1/trash-empty.1',
                                'man/man1/trash-list.1',
                                'man/man1/trash-restore.1',
                                'man/man1/trash-put.1'])],
    tests_require = file("requirements-dev.txt").readlines(),
)

