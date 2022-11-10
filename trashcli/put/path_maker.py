import os


class PathMakerType:
    pass


class AbsolutePaths(PathMakerType):
    pass


class RelativePaths(PathMakerType):
    pass


class PathMaker:
    def calc_parent_path(self, parent, volume_top_dir,
                         path_maker_type,  # type: PathMakerType
                         ):
        if path_maker_type == AbsolutePaths:
            return parent
        if path_maker_type == RelativePaths:
            if (parent == volume_top_dir) or parent.startswith(
                    volume_top_dir + os.path.sep):
                parent = parent[len(volume_top_dir + os.path.sep):]
            return parent
