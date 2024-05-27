from trashcli.fs_impl import RealRemoveFile2
from trashcli.fs_impl import RealRemoveFileIfExists


class FileRemover(RealRemoveFile2, RealRemoveFileIfExists):
    pass
