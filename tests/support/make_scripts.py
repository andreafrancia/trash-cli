import os
from typing import List

from trashcli.path import Path
from textwrap import dedent

from tests.support.project_root import get_project_root
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.fs.script_fs import ScriptFs


def make_scripts():
    return Scripts(RealFs(), get_project_root())

class ScriptPaths:
    def __init__(self,
                 project_root,  # type: Path
                 ):
        self._project_root = project_root

    def script_path_for(self, name):
        return self._project_root / script_path_without_base_dir_for(name)


class Scripts:
    def __init__(self,
                 fs,  # type: ScriptFs
                 project_root,  # type: Path
                 ):
        self.fs = fs
        self.created_scripts = []  # type: List[str]
        self.script_paths = ScriptPaths(project_root)

    def add_script(self, name, module, main_function):
        path = self.script_paths.script_path_for(name)
        script_contents = dedent("""\
            #!/usr/bin/env python
            from __future__ import absolute_import
            import sys
            from %(module)s import %(main_function)s as main
            sys.exit(main())
            """) % locals()
        self.fs.write_file(path, script_contents.encode('utf-8'))
        self.fs.make_file_executable(path)
        self.created_scripts.append(str(script_path_without_base_dir_for(name)))



def script_path_without_base_dir_for(name):
    return Path(os.path.join(name))
