# Copyright (C) 2007-2012 Andrea Francia Trivolzio(PV) Italy

from distutils.core import setup
import sys

def main():
    sys.path.append('.')
    from trashcli import trash
    scripts.add_script('trash'        , 'trashcli.put' , 'main')
    scripts.add_script('trash-put'    , 'trashcli.put' , 'main')
    scripts.add_script('trash-list'   , 'trashcli.cmds', 'list')
    scripts.add_script('trash-restore', 'trashcli.cmds', 'restore')
    scripts.add_script('trash-empty'  , 'trashcli.cmds', 'empty')
    scripts.add_script('trash-rm'     , 'trashcli.rm'  , 'main')
    setup(
        name = 'trash-cli'        , version = trash.version                  ,
        author = 'Andrea Francia' , author_email = 'andrea@andreafrancia.it' ,
        url = 'https://github.com/andreafrancia/trash-cli',
        description = 'Command line interface to FreeDesktop.org Trash.',
        long_description = file("README.rst").read(),
        license = 'GPL v2',
        packages = ['trashcli'],
        scripts = scripts.created_scripts,
        data_files = [('share/man/man1', ['man/man1/trash-empty.1',
                                          'man/man1/trash-list.1',
                                          'man/man1/trash-restore.1',
                                          'man/man1/trash-put.1',
                                          'man/man1/trash-rm.1'])],
    )

from textwrap import dedent
class Scripts:
    def __init__(self, write_file, make_file_executable):
        self.write_file           = write_file
        self.make_file_executable = make_file_executable
        self.created_scripts      = []
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

import os,stat
def make_file_executable(path):
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
def write_file(name, contents):
    file(name, 'w').write(contents)

scripts = Scripts(write_file, make_file_executable)

if __name__ == '__main__':
    main()
