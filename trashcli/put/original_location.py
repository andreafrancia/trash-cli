import os


def parent_realpath(path):
    parent = os.path.dirname(path)
    return os.path.realpath(parent)


class OriginalLocation:
    def __init__(self, parent_realpath, path_maker):
        self.parent_realpath = parent_realpath
        self.path_maker = path_maker

    def for_file(self, path, path_maker_type, volume_top_dir):
        self.normalized_path = os.path.normpath(path)

        basename = os.path.basename(self.normalized_path)
        parent = self.parent_realpath(self.normalized_path)

        parent = self.path_maker.calc_parent_path(parent, volume_top_dir,
                                                  path_maker_type)

        return os.path.join(parent, basename)
