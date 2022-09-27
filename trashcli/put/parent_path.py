import os


def parent_path(path):
    return os.path.realpath(os.path.dirname(path))
