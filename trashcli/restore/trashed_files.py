from typing import Iterable
from typing import NamedTuple
from typing import Optional
from typing import Union

from trashcli.fstab.volumes import Volumes
from trashcli.lib.environ import Environ
from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.parse_trashinfo.parse_deletion_date import parse_deletion_date
from trashcli.parse_trashinfo.parse_original_location import \
    parse_original_location
from trashcli.put.fs.fs import Fs
from trashcli.restore.info_dir_searcher import InfoDirSearcher
from trashcli.restore.restore_logger import RestoreLogger
from trashcli.restore.trash_directories import TrashDirectoriesImpl
from trashcli.restore.trashed_file import TrashedFile


class TrashedFiles:
    def __init__(self,
                 volumes,  # type: Volumes
                 uid,  # type: int
                 environ,  # type: Environ
                 fs,  # type: Fs
                 logger,  # type: RestoreLogger
                 ):
        trash_directories = TrashDirectoriesImpl(volumes, uid, environ)
        info_dir_searcher = InfoDirSearcher(trash_directories, fs)
        self.logger = logger
        self.file_reader = fs
        self.searcher = info_dir_searcher

    def all_trashed_files(self,
                          trash_dir_from_cli,  # type: Optional[str]
                          ):  # type: (...) -> Iterable[TrashedFile]
        for event in self.all_trashed_files_internal(trash_dir_from_cli):
            if type(event) is NonTrashinfoFileFound:
                self.logger.warning("Non .trashinfo file in info dir")
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

    def all_trashed_files_internal(self,
                                   trash_dir_from_cli,  # type: Optional[str]
                                   ):  # type: (...) -> Iterable[Event]
        for info_file in self.searcher.all_file_in_info_dir(trash_dir_from_cli):
            if info_file.type == 'non_trashinfo':
                yield NonTrashinfoFileFound(info_file.path)
            elif info_file.type == 'trashinfo':
                try:
                    contents = self.file_reader.read_file(info_file.path)
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
