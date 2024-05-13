from __future__ import print_function

import argparse
import sys

from six import text_type

from tests.support.project_root import project_root
from tests.support.tools.adapters.real_cal import RealCal
from tests.support.tools.bump_cmd import trash_py_file
from tests.support.tools.version_from_date import dev_version_from_date
from tests.support.tools.version_saver import VersionSaver
from trashcli.put.fs.real_fs import RealFs


def main():
    cmd = SetDevVersionCmd(RealFs(), sys.stdout, sys.stderr, RealCal())
    cmd.run_set_dev_version(sys.argv, project_root())


class SetDevVersionCmd:
    def __init__(self, fs, stdout, stderr, cal):
        self.stdout = stdout
        self.stderr = stderr
        self.cal = cal
        self.version_saver = VersionSaver(fs)

    def run_set_dev_version(self, argv, root):
        parser = argparse.ArgumentParser(prog=argv[0])
        parser.add_argument('ref')
        parser.add_argument('sha')
        args = parser.parse_args(argv[1:])

        self.warn_about_using_underscore_as_ref(args)

        new_version = dev_version_from_date(args.ref, args.sha,
                                            self.cal.today())
        self.version_saver.save_new_version(new_version, trash_py_file(root))

    def warn_about_using_underscore_as_ref(self, args):
        if "-" in args.ref:
            print(text_type(
                "Ref cannot contain '-': %s\n" % args.ref +
                "The reason is because any '-' will be converted to '.' "
                "by setuptools during the egg_info phase that will result in "
                "an error in scripts/make-scripts because it will be not "
                "able to find the .tar.gz file"),
                file=self.stderr)
            sys.exit(1)
