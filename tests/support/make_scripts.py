import os
from textwrap import dedent
from typing import List

from tests.support.project_root import project_root
from trashcli.compat import Protocol
from trashcli.fslib.real_fs_operations import RealWriteFile, \
    RealMakeFileExecutable


def make_scripts():
    class RealScriptFs(ScriptFs):
        write_file = RealWriteFile().write_file
        make_file_executable = RealMakeFileExecutable().make_file_executable
    fs = RealScriptFs()
    return Scripts(fs)

class ScriptFs(Protocol):
    def make_file_executable(self, path):
        raise NotImplementedError

    def write_file(self, name, contents):
        raise NotImplementedError

class Scripts:
    def __init__(self, fs: ScriptFs):
        self.fs = fs
        self.created_scripts = []  # type: List[str]

    def add_script(self,
                   name,  # type: str
                   module,  # type: str
                   main_function,  # type: str
                   ):  # type: (...) -> None
        path = script_path_for(name)
        script_contents = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from %(module)s import %(main_function)s as main
            sys.exit(main())
            """) % locals()
        self.fs.write_file(path, script_contents)
        self.fs.make_file_executable(path)
        self.created_scripts.append(script_path_without_base_dir_for(name))


def script_path_for(name):
    return os.path.join(project_root(), script_path_without_base_dir_for(name))


def script_path_without_base_dir_for(name):  # type: (str) -> str
    return os.path.join(name)
