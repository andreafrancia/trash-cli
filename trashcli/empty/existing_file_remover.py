from trashcli.fslib.real_fs_operations import RealRemoveFile2, RealRemoveFileIfExists


class ExistingFileRemover(RealRemoveFileIfExists, RealRemoveFile2):
    pass
