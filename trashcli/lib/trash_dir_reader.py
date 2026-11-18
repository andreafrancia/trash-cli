from __future__ import absolute_import

import os

from trashcli.fslib.protocols.dir_reader_fs import DirReaderFs


class TrashDirReader:

    def __init__(self,
                 dir_reader, # type: DirReaderFs
                 ):
        self.dir_reader = dir_reader

    def list_trashinfo(self, path):
        info_dir = os.path.join(path, 'info')
        for entry in self.dir_reader.entries_if_dir_exists(info_dir):
            if entry.endswith('.trashinfo'):
                yield os.path.join(info_dir, entry)
