import os

from trashcli.fslib.protocols.atomic_write import AtomicWrite


class RealAtomicWrite(AtomicWrite):
    def atomic_write(self, path, content):
        file_handle = self.open_for_write_in_exclusive_and_create_mode(path)
        os.write(file_handle, content)
        os.close(file_handle)

    def open_for_write_in_exclusive_and_create_mode(self, path):
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
