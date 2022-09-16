from trashcli.fs import FileRemover


class ExistingFileRemover:
    @staticmethod
    def remove_file_if_exists(path):
        return FileRemover.remove_file_if_exists(path)
