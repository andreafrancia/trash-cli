import os

from trashcli.fs import file_size
from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.parse_trashinfo.maybe_parse_deletion_date import \
    maybe_parse_deletion_date


class DeletionDateExtractor:
    def extract_attribute(self, _trashinfo_path, contents):
        return maybe_parse_deletion_date(contents)


class SizeExtractor:
    def extract_attribute(self, trashinfo_path, _contents):
        backup_copy = path_of_backup_copy(trashinfo_path)
        try:
            return str(file_size(backup_copy))
        except FileNotFoundError:
            if os.path.islink(backup_copy):
                return 0
            else:
                raise
