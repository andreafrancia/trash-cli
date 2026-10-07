import os

from trashcli.fslib.listdir_with_complete_path import listdir_with_complete_path
from trashcli.fslib.protocols.listdir_fs import ListdirFs


class InfoFiles:
    def __init__(self,
                 fs,  # type: ListdirFs
                 ):
        self.fs = fs

    def all_info_files(self,
                       path,  # type: str
                       ):
        norm_path = os.path.normpath(path)
        info_dir = os.path.join(norm_path, 'info')
        try:
            for info_file in listdir_with_complete_path(self.fs, info_dir):
                if not os.path.basename(info_file).endswith('.trashinfo'):
                    yield ('non_trashinfo', info_file)
                else:
                    yield ('trashinfo', info_file)
        except OSError:  # when directory does not exist
            pass
