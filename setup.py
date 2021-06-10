# Copyright (C) 2007-2021 Andrea Francia Trivolzio(PV) Italy

from trashcli.fs import read_file, write_file, make_file_executable
from trashcli import trash
from textwrap import dedent


def main():
    scripts = Scripts(write_file, make_file_executable)
    scripts.add_script('trash', 'trashcli.put', 'main')
    scripts.add_script('trash-put', 'trashcli.put', 'main')
    scripts.add_script('trash-list', 'trashcli.list', 'main')
    scripts.add_script('trash-restore', 'trashcli.restore', 'main')
    scripts.add_script('trash-empty', 'trashcli.empty', 'main')
    scripts.add_script('trash-rm', 'trashcli.rm', 'main')
    setup(
        name='trash-cli',
        version=trash.version,
        author='Andrea Francia',
        author_email='andrea@andreafrancia.it',
        url='https://github.com/andreafrancia/trash-cli',
        description='Command line interface to FreeDesktop.org Trash.',
        long_description=read_file("README.rst"),
        license='GPL v2',
        packages=['trashcli'],
        scripts=scripts.created_scripts,
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


class Scripts:
    def __init__(self, write_file, make_file_executable):
        self.write_file = write_file
        self.make_file_executable = make_file_executable
        self.created_scripts = []

    def add_script(self, name, module, main_function):
        script_contents = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from %(module)s import %(main_function)s as main
            sys.exit(main())
            """) % locals()
        self.write_file(name, script_contents)
        self.make_file_executable(name)
        self.created_scripts.append(name)


if __name__ == '__main__':
    from setuptools import setup
    main()
