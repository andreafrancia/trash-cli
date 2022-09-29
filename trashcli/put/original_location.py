import os


def parent_realpath(path):
    parent = os.path.dirname(path)
    return os.path.realpath(parent)


class OriginalLocation:
    def __init__(self, parent_realpath):
        self.parent_realpath = parent_realpath

    def for_file(self, path, path_maker):
        self.normalized_path = os.path.normpath(path)

        basename = os.path.basename(self.normalized_path)
        parent = self.parent_realpath(self.normalized_path)

        parent = path_maker.calc_parent_path(parent)

        return os.path.join(parent, basename)
