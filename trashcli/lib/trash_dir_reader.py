from __future__ import absolute_import

import os

from trashcli.lib.dir_reader import DirReader


class TrashDirReader:

    def __init__(self,
                 dir_reader, # type: DirReader
                 ):
        self.dir_reader = dir_reader

    def list_orphans(self, path):
        info_dir = os.path.join(path, 'info')
        files_dir = os.path.join(path, 'files')
        for entry in self.dir_reader.entries_if_dir_exists(files_dir):
            trashinfo_path = os.path.join(info_dir, entry + '.trashinfo')
            file_path = os.path.join(files_dir, entry)
            if not self.dir_reader.exists(trashinfo_path):
                yield file_path

    def list_trashinfo(self, path):
        info_dir = os.path.join(path, 'info')
        for entry in self.dir_reader.entries_if_dir_exists(info_dir):
            if entry.endswith('.trashinfo'):
                yield os.path.join(info_dir, entry)
