from __future__ import print_function

import os
from typing import List
from typing import NamedTuple

from trashcli.fslib.protocols.dir_reader_fs import DirReaderFs
from trashcli.lib.action import Action
from trashcli.lib.inconsistencies import inconsistencies_check_hint
from trashcli.lib.inconsistencies import inconsistencies_found
from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.lib.printable import printable
from trashcli.lib.sanitize import shell_escape, quoting_wanted
from trashcli.list.extractors import DeletionDateExtractor
from trashcli.list.extractors import SizeExtractor
from trashcli.list.extractors import SizeExtractorFs
from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.trash_dirs_scanner import trash_dir_found
from trashcli.trash_dirs_scanner import \
    trash_dir_skipped_because_parent_is_symlink
from trashcli.trash_dirs_scanner import \
    trash_dir_skipped_because_parent_not_sticky


def quote_nothing(name):
    return name


class ListTrashArgs(
    NamedTuple('ListTrashArgs', [
        ('trash_dirs', List[str]),
        ('attribute_to_print', str),
        ('show_files', bool),
        ('all_users', bool),
    ])):
    pass


class DoctorArgs(
    NamedTuple('DoctorArgs', [
        ('trash_dirs', List[str]),
        ('all_users', bool),
    ])):
    pass


class ListTrashAction(Action):
    def __init__(self,
                 environ,
                 uid,
                 selector,
                 out,
                 err,
                 dir_reader,
                 content_reader,
                 file_reader,  # type: SizeExtractorFs
                 ):
        self.environ = environ
        self.uid = uid
        self.selector = selector
        self.out = out
        self.err = err
        self.dir_reader = dir_reader
        self.content_reader = content_reader
        self.file_reader = file_reader

    def run_action(self,
                   args,  # type: ListTrashArgs
                   ):
        quote = shell_escape if quoting_wanted(self.out, self.environ) \
            else quote_nothing
        found_inconsistencies = False
        for message in ListTrash(self.environ,
                                 self.uid,
                                 self.selector,
                                 self.dir_reader,
                                 self.content_reader,
                                 quote,
                                 self.file_reader).list_all_trash(args):
            if isinstance(message, InconsistenciesSummary):
                found_inconsistencies = True
            self.print_event(message)
        if found_inconsistencies:
            print(printable(inconsistencies_check_hint()), file=self.err)

    def print_event(self, event):
        if isinstance(event, Error):
            print(printable(event.error), file=self.err)
        elif isinstance(event, Output):
            print(printable(event.message), file=self.out)
        elif isinstance(event, Inconsistency):
            print(printable(event.message), file=self.out)
        elif isinstance(event, InconsistenciesSummary):
            print(printable(event.message), file=self.err)


class DoctorAction(Action):
    def __init__(self,
                 environ,
                 uid,
                 selector,
                 out,
                 err,
                 dir_reader,
                 content_reader,
                 ):
        self.environ = environ
        self.uid = uid
        self.selector = selector
        self.out = out
        self.err = err
        self.dir_reader = dir_reader
        self.content_reader = content_reader

    def run_action(self,
                   args,  # type: DoctorArgs
                   ):
        trash_dirs = self.selector.select(args.all_users,
                                          args.trash_dirs,
                                          self.environ,
                                          self.uid)
        for event, event_args in trash_dirs:
            if event == trash_dir_found:
                path, volume = event_args
                for msg in self._doctor_dir_events(path):
                    self.print_event(msg)
            elif event == trash_dir_skipped_because_parent_not_sticky:
                path, = event_args
                self.print_event(Error(
                    top_trashdir_skipped_because_parent_not_sticky(path)))
            elif event == trash_dir_skipped_because_parent_is_symlink:
                path, = event_args
                self.print_event(Error(
                    top_trashdir_skipped_because_parent_is_symlink(path)))

    def _doctor_dir_events(self, path):
        info_dir = os.path.join(path, 'info')
        for entry in self.dir_reader.entries_if_dir_exists(info_dir):
            entry_path = os.path.join(info_dir, entry)
            if entry.endswith('.trashinfo'):
                try:
                    contents = self.content_reader.read_file(entry_path)
                except IOError as e:
                    yield Error(str(e))
                else:
                    try:
                        parse_path(contents)
                    except ParseError:
                        yield Inconsistency(
                            print_parse_path_error(entry_path))
            else:
                yield Inconsistency(
                    print_non_trashinfo_error(entry_path))

    def print_event(self, event):
        if isinstance(event, Error):
            print(printable(event.error), file=self.err)
        elif isinstance(event, Inconsistency):
            print(printable(event.message), file=self.out)
        else:
            raise RuntimeError()


class ListTrash:
    def __init__(self,
                 environ,
                 uid,
                 selector,
                 dir_reader,  # type: DirReaderFs
                 content_reader,
                 quote,
                 file_reader,  # type: SizeExtractorFs
                 ):
        self.environ = environ
        self.uid = uid
        self.selector = selector
        self.dir_reader = dir_reader
        self.content_reader = content_reader
        self.quote = quote
        self.file_reader = file_reader

    def list_all_trash(self,
                       args,  # type: ListTrashArgs
                       ):
        extractors = {
            'deletion_date': DeletionDateExtractor(),
            'size': SizeExtractor(self.file_reader),
        }
        user_specified_trash_dirs = args.trash_dirs
        extractor = extractors[args.attribute_to_print]
        show_files = args.show_files
        all_users = args.all_users
        trash_dirs = self.selector.select(all_users,
                                          user_specified_trash_dirs,
                                          self.environ,
                                          self.uid)
        for event, event_args in trash_dirs:
            if event == trash_dir_found:
                path, volume = event_args
                for msg in self._list_trash_dir(path, volume, extractor,
                                                show_files):
                    yield msg
            elif event == trash_dir_skipped_because_parent_not_sticky:
                path, = event_args
                msg = Error(
                    top_trashdir_skipped_because_parent_not_sticky(path))
                yield msg
            elif event == trash_dir_skipped_because_parent_is_symlink:
                path, = event_args
                msg = Error(
                    top_trashdir_skipped_because_parent_is_symlink(path))
                yield msg

    def _list_trash_dir(self, path, volume, extractor, show_files):
        found_inconsistencies = False
        for msg in self._trash_dir_events(path, volume, extractor,
                                          show_files):
            if isinstance(msg, Inconsistency):
                found_inconsistencies = True
            elif isinstance(msg, Output):
                yield msg
            else:
                yield msg
        if found_inconsistencies:
            yield InconsistenciesSummary(
                inconsistencies_found(path, self.environ))

    def _trash_dir_events(self, path, volume, extractor, show_files):
        info_dir = os.path.join(path, 'info')
        for entry in self.dir_reader.entries_if_dir_exists(info_dir):
            entry_path = os.path.join(info_dir, entry)
            if entry.endswith('.trashinfo'):
                for msg in self._print_trashinfo(volume, entry_path,
                                                 extractor, show_files):
                    yield msg
            else:
                yield Inconsistency(
                    print_non_trashinfo_error(entry_path))

    def _print_trashinfo(self,
                         volume,
                         trashinfo_path,
                         extractor,
                         show_files):
        try:
            contents = self.content_reader.read_file(trashinfo_path)
        except IOError as e:
            yield Error(str(e))
        else:
            try:
                relative_location = parse_path(contents)
            except ParseError:
                yield Inconsistency(
                    print_parse_path_error(trashinfo_path))
            else:
                attribute = extractor.extract_attribute(trashinfo_path,
                                                        contents)
                original_location = self.quote(
                    os.path.join(volume, relative_location))

                if show_files:
                    original_file = self.quote(
                        path_of_backup_copy(trashinfo_path))
                    line = format_line2(attribute, original_location,
                                        original_file)
                else:
                    line = format_line(attribute, original_location)
                yield Output(line)


class Event:
    pass


class Error(Event):
    def __init__(self, error):
        self.error = error


class Output(Event):
    def __init__(self, message):
        self.message = message


class Inconsistency(Event):
    def __init__(self, message):
        self.message = message


class InconsistenciesSummary(Event):
    def __init__(self, message):
        self.message = message


def top_trashdir_skipped_because_parent_is_symlink(trashdir):
    return "TrashDir skipped because parent is symlink: %s" % trashdir


def top_trashdir_skipped_because_parent_not_sticky(trashdir):
    return "TrashDir skipped because parent not sticky: %s" % trashdir


def print_parse_path_error(offending_file):
    return "Parse Error: %s: Unable to parse Path." % offending_file


def print_non_trashinfo_error(offending_file):
    return "Non .trashinfo file in info dir: %s" % offending_file


def format_line(attribute, original_location):
    return "%s %s" % (attribute, original_location)


def format_line2(attribute, original_location, original_file):
    return "%s %s -> %s" % (attribute, original_location, original_file)
