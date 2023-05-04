import os

from trashcli.put.fs.parent_realpath import ParentRealpath
from trashcli.put.path_maker import PathMaker, PathMakerType


class OriginalLocation:
    def __init__(self,
                 parent_realpath,  # type: ParentRealpath
                 path_maker,  # type: PathMaker
                 ):
        self.parent_realpath = parent_realpath
        self.path_maker = path_maker

    def for_file(self,
                 path,
                 path_maker_type, # type: PathMakerType
                 volume_top_dir,
                 ): # type: (...) -> str
        normalized_path = os.path.normpath(path)
        basename = os.path.basename(normalized_path)
        parent = self.parent_realpath.parent_realpath(normalized_path)
        parent = self.path_maker.calc_parent_path(parent, volume_top_dir,
                                                  path_maker_type)

        return os.path.join(parent, basename)
