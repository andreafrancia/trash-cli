import os

from trashcli.restore.file_system import ListingFileSystem


class InfoFiles:
    def __init__(self,
                 fs,  # type: ListingFileSystem
                 ):
        self.fs = fs

    def all_info_files(self, path):
        norm_path = os.path.normpath(path)
        info_dir = os.path.join(norm_path, 'info')
        try:
            for info_file in self.fs.list_files_in_dir(info_dir):
                if not os.path.basename(info_file).endswith('.trashinfo'):
                    yield ('non_trashinfo', info_file)
                else:
                    yield ('trashinfo', info_file)
        except OSError:  # when directory does not exist
            pass
