from trashcli.fs import FileReader
from trashcli.fs import ListFilesInDir
from trashcli.fs import MkDirs
from trashcli.fs import PathExists
from trashcli.fs import RemoveFile
from trashcli.fs import Move


class RestoreFs(ListFilesInDir,
                RemoveFile,
                Move,
                FileReader,
                PathExists,
                MkDirs,
                ):
    pass
