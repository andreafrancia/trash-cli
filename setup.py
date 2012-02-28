# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

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
            'trash-list    = trashcli.cmds:list',
            'trash-put     = trashcli.cmds:put',
            'restore-trash = trashcli.cmds:restore',
            'trash-empty   = trashcli.cmds:empty'
        ]
    },
    data_files = [('man/man1', ['man/man1/trash-empty.1',
                                'man/man1/trash-list.1',
                                'man/man1/trash-restore.1',
                                'man/man1/trash-put.1'])],
    tests_require = file("requirements-dev.txt").readlines(),
)

