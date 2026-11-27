from trashcli.fslib.protocols.read_file import ReadFile
from trashcli.fslib.real.read_whole_file import read_whole_file


class RealReadFile(ReadFile):
    def read_file(self, path):  # type: (str) -> str
        return read_whole_file(path)
