from trashcli.compat import Protocol
from trashcli.fslib.protocols.file_size import FileSize
from trashcli.fslib.protocols.is_sym_link import IsSymLink
from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.parse_trashinfo.maybe_parse_deletion_date import \
    maybe_parse_deletion_date

class DeletionDateExtractor:
    def extract_attribute(self, _trashinfo_path, contents):
        return maybe_parse_deletion_date(contents)


class SizeExtractorFs(FileSize, IsSymLink, Protocol):
    pass


class SizeExtractor:
    def __init__(self,
                 fs,  # type: SizeExtractorFs
                 ):
        self.fs = fs

    def extract_attribute(self, trashinfo_path, _contents):
        backup_copy = path_of_backup_copy(trashinfo_path)
        try:
            return str(self.fs.file_size(backup_copy))
        except FileNotFoundError:
            if self.fs.is_symlink(backup_copy):
                return 0
            else:
                raise
