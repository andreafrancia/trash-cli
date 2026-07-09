from trashcli.fslib.real_fs_operations import RealRemoveFile2, \
    RealRemoveFileIfExists


class RealRemoverFs(RealRemoveFile2, RealRemoveFileIfExists):
    pass
