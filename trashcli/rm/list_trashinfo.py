# Copyright (C) 2011-2021 Andrea Francia Bereguardo(PV) Italy
import os
from typing import Iterable

from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError


class ListTrashinfos:
    def __init__(self,
                 fs,  # type: ListTrashinfosFs
                 ):
        self.fs = fs  # type: ListTrashinfosFs

    def list_from_volume_trashdir(self, trashdir_path, volume):
        for trashinfo_path in TrashDirReader(self.fs).list_trashinfo(
                trashdir_path):
            trashinfo = self.fs.read_file(trashinfo_path)
            try:
                path = parse_path(trashinfo)
            except ParseError:
                yield 'unable_to_parse_path', trashinfo_path
            else:
                complete_path = os.path.join(volume, path)
                yield 'trashed_file', (complete_path, trashinfo_path)

from abc import abstractmethod
from trashcli.compat import Protocol
from typing import List

class ListTrashinfosFs(Protocol):
    @abstractmethod
    def read_file(self, path):
        raise NotImplementedError()

    @abstractmethod
    def path_exists(self, path):  # type: (str) -> bool
        raise NotImplementedError

    @abstractmethod
    def listdir(self, path):  # type: (str) -> List[str]
        raise NotImplementedError
