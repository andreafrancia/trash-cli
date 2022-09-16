from trashcli.empty.console import Console
from trashcli.fs import FileRemover


class FileRemoveWithErrorHandling:
    def __init__(self, file_remover, console
                 ):  # type: (FileRemover, Console) -> None
        self.file_remover = file_remover
        self.console = console

    def remove_file2(self, path):
        try:
            self.file_remover.remove_file(path)
        except OSError:
            self.console.print_cannot_remove_error(path)

    def remove_file_if_exists2(self, path):
        try:
            return self.file_remover.remove_file_if_exists(path)
        except OSError:
            self.console.print_cannot_remove_error(path)
