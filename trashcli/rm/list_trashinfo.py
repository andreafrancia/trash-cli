# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os

from trashcli.fs import FileReader
from trashcli.lib.dir_reader import DirReader
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError


class ListTrashinfos:
    def __init__(self,
                 file_content_reader,  # type: FileReader
                 trash_dir_reader,  # type: TrashDirReader
                 ):
        self.trash_dir_reader = trash_dir_reader
        self.file_content_reader = file_content_reader

    def list_from_volume_trashdir(self, trashdir_path, volume):
        for trashinfo_path in self.trash_dir_reader.list_trashinfo(
                trashdir_path):
            trashinfo = self.file_content_reader.read_file(trashinfo_path)
            try:
                path = parse_path(trashinfo)
            except ParseError:
                yield 'unable_to_parse_path', trashinfo_path
            else:
                complete_path = os.path.join(volume, path)
                yield 'trashed_file', (complete_path, trashinfo_path)

    @staticmethod
    def make(file_content_reader,  # type: FileReader
             dir_reader,  # type: DirReader
             ):
        trash_dir_reader = TrashDirReader(dir_reader)
        return ListTrashinfos(file_content_reader, trash_dir_reader)
