# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
import abc

import six

from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.lib.dir_reader import DirReader


@six.add_metaclass(abc.ABCMeta)
class FileContentReader:
    @abc.abstractmethod
    def contents_of(self, path):
        raise NotImplementedError()


class ListTrashinfos:
    def __init__(self,
                 file_content_reader,  # type: FileContentReader
                 trash_dir_reader,  # type: TrashDirReader
                 ):
        self.trash_dir_reader = trash_dir_reader
        self.file_content_reader = file_content_reader

    def list_from_volume_trashdir(self, trashdir_path, volume):
        for trashinfo_path in self.trash_dir_reader.list_trashinfo(
                trashdir_path):
            trashinfo = self.file_content_reader.contents_of(trashinfo_path)
            try:
                path = parse_path(trashinfo)
            except ParseError:
                yield 'unable_to_parse_path', trashinfo_path
            else:
                complete_path = os.path.join(volume, path)
                yield 'trashed_file', (complete_path, trashinfo_path)

    @staticmethod
    def make(file_content_reader,  # type: FileContentReader
             dir_reader,  # type: DirReader
             ):
        trash_dir_reader = TrashDirReader(dir_reader)
        return ListTrashinfos(file_content_reader, trash_dir_reader)
