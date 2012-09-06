# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

import ez_setup; ez_setup.use_setuptools()
from setuptools import setup

import sys
sys.path.append('.')
from trashcli import trash

setup(
    name = 'trash-cli'        , version = trash.version                  ,
    author = 'Andrea Francia' , author_email = 'andrea@andreafrancia.it' ,
    url = 'https://github.com/andreafrancia/trash-cli',
    description = 'Command line interface to FreeDesktop.org Trash.',
    long_description = file("README.rst").read(),
    license = 'GPL v2',
    packages = ['trashcli', 'integration_tests', 'unit_tests'],
    test_suite = "nose.collector",
    entry_points = {
        'console_scripts' : [
            'trash-list    = trashcli.cmds:list',
            'trash         = trashcli.cmds:put',
            'trash-put     = trashcli.cmds:put',
            'restore-trash = trashcli.cmds:restore',
            'trash-empty   = trashcli.cmds:empty',
            'trash-rm      = trashcli.rm:main',
        ]
    },
    data_files = [('share/man/man1', ['man/man1/trash-empty.1',
                                      'man/man1/trash-list.1',
                                      'man/man1/restore-trash.1',
                                      'man/man1/trash-put.1'])],
    tests_require = file("requirements-dev.txt").readlines(),
)

