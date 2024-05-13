import os

from tests.support.tools.version_from_date import version_from_date
from tests.support.tools.version_saver import VersionSaver


def trash_py_file(root):
    return os.path.join(root, 'trashcli', 'trash.py')


class BumpCmd:
    def __init__(self, os_system, print_func, fs, cal):
        self.system = os_system
        self.print_func = print_func
        self.fs = fs
        self.cal = cal

    def run_bump(self, root, args):
        # https://unix.stackexchange.com/questions/155046/determine-if-git-working-directory-is-clean-from-a-script/394674#394674
        if self.system("git diff-index --quiet HEAD") != 0:
            self.print_func("Dirty")
            exit(1)

        new_version = version_from_date(self.cal.today())

        if not '--dry-run' in args:
            VersionSaver(self.fs).save_new_version(new_version,
                                                   trash_py_file(root))

        system = self.print_func if '--dry-run' in args else self.system
        system("git commit -m \"Bump version to '%s'\" -a" % new_version)
