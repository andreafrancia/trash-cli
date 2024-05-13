import os
import sys

from tests.support.project_root import project_root
from tests.support.tools.adapters.real_cal import RealCal
from tests.support.tools.bump_cmd import BumpCmd
from trashcli.put.fs.real_fs import RealFs


def main():
    print(project_root())
    bump_cmd = BumpCmd(os.system, print, RealFs(), RealCal())
    bump_cmd.run_bump(project_root(), sys.argv[1:])
