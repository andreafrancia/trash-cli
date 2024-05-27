from trashcli.fs_impl import RealRemoveFileIfExists
from trashcli.fs_impl import RealRemoveFile2


class ExistingFileRemover(RealRemoveFileIfExists, RealRemoveFile2):
    pass
