import os


class PathMaker:
    def calc_parent_path(self, parent, volume_top_dir, path_maker_type):
        if path_maker_type == PathMakerType.absolute_paths:
            return parent
        if path_maker_type == PathMakerType.relative_paths:
            if (parent == volume_top_dir) or parent.startswith(
                    volume_top_dir + os.path.sep):
                parent = parent[len(volume_top_dir + os.path.sep):]
            return parent


class PathMakerType:
    absolute_paths = 'absolute_paths'
    relative_paths = 'relative_paths'
