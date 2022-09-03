import os
from textwrap import dedent

from trashcli import base_dir
from trashcli.fs import write_file, make_file_executable


def make_scripts():
    return Scripts(write_file, make_file_executable)


class Scripts:
    def __init__(self, write_file, make_file_executable):
        self.write_file = write_file
        self.make_file_executable = make_file_executable
        self.created_scripts = []

    def add_script(self, name, module, main_function):
        path = script_path_for(name)
        script_contents = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from %(module)s import %(main_function)s as main
            sys.exit(main())
            """) % locals()
        self.write_file(path, script_contents)
        self.make_file_executable(path)
        self.created_scripts.append(script_path_without_base_dir_for(name))


def script_path_for(name):
    return os.path.join(base_dir, script_path_without_base_dir_for(name))


def script_path_without_base_dir_for(name):
    return os.path.join(name)
