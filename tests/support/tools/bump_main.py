import os
import sys

from tests.support.project_root import get_project_root
from tests.support.tools.adapters.real_cal import RealCal
from tests.support.tools.bump_cmd import BumpCmd
from trashcli.put.fs.real_fs import RealFs


def main():
    project_root = get_project_root()
    print(project_root)
    bump_cmd = BumpCmd(os.system, print, RealFs(), RealCal())
    bump_cmd.run_bump(project_root, sys.argv[1:])
