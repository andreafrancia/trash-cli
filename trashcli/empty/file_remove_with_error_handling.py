class FileRemoveWithErrorHandling:
    def __init__(self, file_remover, on_error):
        self.file_remover = file_remover
        self.on_error = on_error

    def remove_file(self, path):
        try:
            return self.file_remover.remove_file(path)
        except OSError:
            self.on_error(path)

    def remove_file_if_exists(self, path):
        try:
            return self.file_remover.remove_file_if_exists(path)
        except OSError:
            self.on_error(path)
