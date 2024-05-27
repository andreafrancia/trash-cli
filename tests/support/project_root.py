import os

from trashcli.path import Path


def get_project_root():  # type: () -> Path
    this_file = os.path.realpath(__file__)
    support_dir = os.path.dirname(this_file)
    tests_dir = os.path.dirname(support_dir)
    return Path(os.path.dirname(tests_dir))
