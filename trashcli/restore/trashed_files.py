from logging import Logger
from typing import Optional, Iterable, NamedTuple, Union

from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date
from trashcli.parse_trashinfo.parse_original_location import \
    parse_original_location
from trashcli.restore.file_system import FileReader
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.trashed_file import TrashedFile


class TrashedFiles:
    def __init__(self,
                 logger,  # type: Logger
                 file_reader,  # type: FileReader
                 searcher,  # type: InfoDirSearcher
                 ):
        self.logger = logger
        self.file_reader = file_reader
        self.searcher = searcher

    def all_trashed_files(self,
                          trash_dir_from_cli,  # type: Optional[str]
                          ):  # type: (...) -> Iterable[TrashedFile]
        for event in self.all_trashed_files_internal(trash_dir_from_cli):
            if type(event) is NonTrashinfoFileFound:
                self.logger.warning("Non .trashinfo file in info dir")
            elif type(event) is NonParsableTrashInfo:
                self.logger.warning(
                    "Non parsable trashinfo file: %s, because %s" %
                    event.path, event.reason)
            elif type(event) is IOErrorReadingTrashInfo:
                self.logger.warning(str(event))
            elif type(event) is TrashedFileFound:
                yield event.trashed_file
            else:
                raise RuntimeError()

    def all_trashed_files_internal(self,
                                   trash_dir_from_cli,  # type: Optional[str]
                                   ):  # type: (...) -> Iterable[Event]
        for info_file in self.searcher.all_file_in_info_dir(trash_dir_from_cli):
            if info_file.type == 'non_trashinfo':
                yield NonTrashinfoFileFound(info_file.path)
            elif info_file.type == 'trashinfo':
                try:
                    contents = self.file_reader.contents_of(info_file.path)
                    original_location = parse_original_location(contents,
                                                                info_file.volume)
                    deletion_date = parse_deletion_date(contents)
                    backup_file_path = path_of_backup_copy(info_file.path)
                    trashedfile = TrashedFile(original_location,
                                              deletion_date,
                                              info_file.path,
                                              backup_file_path)
                    yield TrashedFileFound(trashedfile)
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
    TrashedFileFound,
    NonParsableTrashInfo,
    IOErrorReadingTrashInfo]
