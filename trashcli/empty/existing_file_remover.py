from trashcli.fs import RealRemoveFileIfExists, RealRemoveFile2


class ExistingFileRemover(RealRemoveFileIfExists, RealRemoveFile2):
    pass
