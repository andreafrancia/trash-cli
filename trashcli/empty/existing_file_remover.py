from trashcli.fslib.real.real_remove_file2 import RealRemoveFile2
from trashcli.fslib.real.real_remove_file_if_exists import RealRemoveFileIfExists


class ExistingFileRemover(RealRemoveFileIfExists, RealRemoveFile2):
    pass
