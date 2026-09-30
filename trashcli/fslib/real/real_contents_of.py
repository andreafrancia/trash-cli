from trashcli.fslib.protocols.contents_of import ContentsOf
from trashcli.fslib.real.read_whole_file import read_whole_file


class RealContentsOf(ContentsOf):
    def contents_of(self, path):
        return read_whole_file(path)
