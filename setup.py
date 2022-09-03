# Copyright (C) 2007-2021 Andrea Francia Trivolzio(PV) Italy

from trashcli.fs import read_file


def main():
    setup(
        author='Andrea Francia',
        author_email='andrea@andreafrancia.it',
        url='https://github.com/andreafrancia/trash-cli',
        description='Command line interface to FreeDesktop.org Trash.',
        long_description=read_file("README.rst"),
        license='GPL v2',
        packages=['trashcli'],
        data_files=[('share/man/man1', ['man/man1/trash-empty.1',
                                        'man/man1/trash-list.1',
                                        'man/man1/trash-restore.1',
                                        'man/man1/trash.1',
                                        'man/man1/trash-put.1',
                                        'man/man1/trash-rm.1'])],
        install_requires=[
            'psutil',
        ],
    )


if __name__ == '__main__':
    from setuptools import setup

    main()
