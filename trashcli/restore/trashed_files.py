from typing import Iterable, List, Mapping, TypeVar
from typing import NamedTuple
from typing import Optional
from typing import Union

from trashcli.lib.inconsistencies import inconsistencies_found
from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date
from trashcli.parse_trashinfo.parse_original_location import \
    OriginalLocationParser
from trashcli.parse_trashinfo.parser_error import UnableToParsePath
from trashcli.restore.fs.protocols.file_reader_fs import FileReaderFs
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.restore_logger import RestoreLogger
from trashcli.restore.trashed_file import TrashedFile

# make Self available in Python < 3.11
Self = TypeVar('Self', bound= 'TrashedFiles')

class TrashedFiles:
    def __init__(self,  # type: Self
                 logger,  # type: RestoreLogger
                 file_reader,  # type: FileReaderFs
                 searcher,  # type: InfoDirSearcher
                 environ,  # type: Mapping[str, str]
                 ):
        self.logger = logger
        self.file_reader = file_reader
        self.searcher = searcher
        self.environ = environ
        self.original_location_parser = OriginalLocationParser()

    def all_trashed_files(self,  # type: Self
                          trash_dir_from_cli,  # type: Optional[str]
                          ):  # type: (...) -> Iterable[TrashedFile]
        inconsistent_trash_dirs = []  # type: List[str]
        for event in self._all_trashed_files_internal(trash_dir_from_cli):
            if isinstance(event, (NonTrashinfoFileFound, MalformedTrashInfo)):
                if event.trash_dir not in inconsistent_trash_dirs:
                    inconsistent_trash_dirs.append(event.trash_dir)
            elif type(event) is NonParsableTrashInfo:
                self.logger.warning(
                    "Non parsable trashinfo file: %s, because %s" %
                    (event.path, event.reason))
            elif type(event) is IOErrorReadingTrashInfo:
                self.logger.warning(str(event))
            elif type(event) is TrashedFileFound:
                yield event.trashed_file
            else:
                raise RuntimeError()
        for trash_dir in inconsistent_trash_dirs:
            self.logger.warning(inconsistencies_found(trash_dir, self.environ))

    def _all_trashed_files_internal(self,  # type: Self
                                    trash_dir_from_cli,  # type: Optional[str]
                                    ):  # type: (...) -> Iterable[Event]
        for info_file in self.searcher.all_file_in_info_dir(trash_dir_from_cli):
            if info_file.type == 'non_trashinfo':
                yield NonTrashinfoFileFound(info_file.path,
                                            info_file.trash_dir)
            elif info_file.type == 'trashinfo':
                try:
                    contents = self.file_reader.read_file(info_file.path)
                    original_location = self.original_location_parser \
                        .parse_original_location(contents, info_file.volume,
                                                 info_file.trash_dir)
                    deletion_date = parse_deletion_date(contents)
                    backup_file_path = path_of_backup_copy(info_file.path)
                    trashedfile = TrashedFile(original_location,
                                              deletion_date,
                                              info_file.path,
                                              backup_file_path)
                    yield TrashedFileFound(trashedfile)
                except UnableToParsePath:
                    yield MalformedTrashInfo(info_file.path,
                                             info_file.trash_dir)
                except ValueError as e:
                    yield NonParsableTrashInfo(info_file.path, e)
                except IOError as e:
                    yield IOErrorReadingTrashInfo(info_file.path, str(e))
            else:
                raise RuntimeError("Unexpected file type: %s: %s",
                                   info_file.type, info_file.path)


class NonTrashinfoFileFound(
    NamedTuple('NonTrashinfoFileFound', [
        ('path', str),
        ('trash_dir', str),
    ])): pass


class MalformedTrashInfo(
    NamedTuple('MalformedTrashInfo', [
        ('path', str),
        ('trash_dir', str),
    ])): pass


class TrashedFileFound(
    NamedTuple('TrashedFileFound', [
        ('trashed_file', TrashedFile),
    ])): pass


class NonParsableTrashInfo(
    NamedTuple('NonParsableTrashInfo', [
        ('path', str),
        ('reason', Exception),
    ])): pass


class IOErrorReadingTrashInfo(
    NamedTuple('IOErrorReadingTrashInfo', [
        ('path', str),
        ('error', str),
    ])): pass


Event = Union[
    NonTrashinfoFileFound,
    MalformedTrashInfo,
    TrashedFileFound,
    NonParsableTrashInfo,
    IOErrorReadingTrashInfo]
