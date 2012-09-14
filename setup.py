# Copyright (C) 2007-2012 Andrea Francia Trivolzio(PV) Italy

from distutils.core import setup
import sys

def main():
    sys.path.append('.')
    from trashcli import trash
    bin_dir.add_script('trash-list'   , 'trashcli.cmds', 'list')
    bin_dir.add_script('trash'        , 'trashcli.cmds', 'put')
    bin_dir.add_script('trash-put'    , 'trashcli.cmds', 'put')
    bin_dir.add_script('restore-trash', 'trashcli.cmds', 'restore')
    bin_dir.add_script('trash-empty'  , 'trashcli.cmds', 'empty')
    bin_dir.add_script('trash-rm'     , 'trashcli.rm'  , 'main')
    setup(
        name = 'trash-cli'        , version = trash.version                  ,
        author = 'Andrea Francia' , author_email = 'andrea@andreafrancia.it' ,
        url = 'https://github.com/andreafrancia/trash-cli',
        description = 'Command line interface to FreeDesktop.org Trash.',
        long_description = file("README.rst").read(),
        license = 'GPL v2',
        packages = ['trashcli'],
        scripts = bin_dir.created_scripts,
        data_files = [('share/man/man1', ['man/man1/trash-empty.1',
                                          'man/man1/trash-list.1',
                                          'man/man1/restore-trash.1',
                                          'man/man1/trash-put.1',
                                          'man/man1/trash-rm.1'])],
    )

from textwrap import dedent
class BinDir:
    def __init__(self, write_file, make_file_executable, make_dir):
        self.write_file           = write_file
        self.make_file_executable = make_file_executable
        self.make_dir             = make_dir
        self.created_scripts      = []
    def add_script(self, name, module, main_function):
        script_contents = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from %(module)s import %(main_function)s as main
            sys.exit(main())
            """) % locals()
        self.make_dir('bin')
        executable = 'bin/' + name
        self.write_file(executable, script_contents)
        self.make_file_executable(executable)
        self.created_scripts.append(executable)

import os,stat
def make_file_executable(path):
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
def write_file(name, contents):
    file(name, 'w').write(contents)
def make_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

bin_dir = BinDir(write_file, make_file_executable, make_dir)

if __name__ == '__main__':
    main()
