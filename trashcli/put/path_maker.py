import os
from typing import Union, Type


class AbsolutePaths:
    pass


class RelativePaths:
    pass


PathMakerType = Union[Type[AbsolutePaths], Type[RelativePaths]]


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
