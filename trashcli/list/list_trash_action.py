from __future__ import print_function

import os
from typing import List
from typing import NamedTuple

from trashcli.lib.dir_reader import DirReader
from trashcli.lib.path_of_backup_copy import path_of_backup_copy
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.list.extractors import DeletionDateExtractor
from trashcli.list.extractors import SizeExtractor
from trashcli.parse_trashinfo.parse_path import parse_path
from trashcli.parse_trashinfo.parser_error import ParseError
from trashcli.trash_dirs_scanner import trash_dir_found
from trashcli.trash_dirs_scanner import \
    trash_dir_skipped_because_parent_is_symlink
from trashcli.trash_dirs_scanner import \
    trash_dir_skipped_because_parent_not_sticky


class ListTrashArgs(
    NamedTuple('ListTrashArgs', [
        ('trash_dirs', List[str]),
        ('attribute_to_print', str),
        ('show_files', bool),
        ('all_users', bool),
    ])):
    pass


class ListTrashAction:
    def __init__(self,
                 environ,
                 uid,
                 selector,
                 out,
                 err,
                 dir_reader,
                 content_reader
                 ):
        self.environ = environ
        self.uid = uid
        self.selector = selector
        self.out = out
        self.err = err
        self.dir_reader = dir_reader
        self.content_reader = content_reader

    def run_action(self,
                   args, # type: ListTrashArgs
                   ):
        for message in ListTrash(self.environ,
                                 self.uid,
                                 self.selector,
                                 self.dir_reader,
                                 self.content_reader).list_all_trash(args):
            self.print_event(message)

    def print_event(self, event):
        if isinstance(event, Error):
            print(event.error, file=self.err)
        elif isinstance(event, Output):
            print(event.message, file=self.out)


class ListTrash:
    def __init__(self,
                 environ,
                 uid,
                 selector,
                 dir_reader,  # type: DirReader
                 content_reader,
                 ):
        self.environ = environ
        self.uid = uid
        self.selector = selector
        self.dir_reader = dir_reader
        self.content_reader = content_reader

    def list_all_trash(self,
                       args,  # type: ListTrashArgs
                       ):
        extractors = {
            'deletion_date': DeletionDateExtractor(),
            'size': SizeExtractor(),
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
                trash_dir = TrashDirReader(self.dir_reader)
                for trash_info in trash_dir.list_trashinfo(path):
                    for msg in self._print_trashinfo(volume, trash_info,
                                                     extractor, show_files):
                        yield msg
            elif event == trash_dir_skipped_because_parent_not_sticky:
                path, = event_args
                msg = Error(
                    self.top_trashdir_skipped_because_parent_not_sticky(path))
                yield msg
            elif event == trash_dir_skipped_because_parent_is_symlink:
                path, = event_args
                msg = Error(
                    self.top_trashdir_skipped_because_parent_is_symlink(path))
                yield msg

    def _print_trashinfo(self,
                         volume,
                         trashinfo_path,
                         extractor,
                         show_files):
        try:
            contents = self.content_reader.contents_of(trashinfo_path)
        except IOError as e:
            yield Error(str(e))
        else:
            try:
                relative_location = parse_path(contents)
            except ParseError:
                yield Error(self.print_parse_path_error(trashinfo_path))
            else:
                attribute = extractor.extract_attribute(trashinfo_path,
                                                        contents)
                original_location = os.path.join(volume, relative_location)

                if show_files:
                    original_file = path_of_backup_copy(trashinfo_path)
                    line = format_line2(attribute, original_location,
                                        original_file)
                else:
                    line = format_line(attribute, original_location)
                yield Output(line)

    def top_trashdir_skipped_because_parent_is_symlink(self, trashdir):
        return "TrashDir skipped because parent is symlink: %s" % trashdir

    def top_trashdir_skipped_because_parent_not_sticky(self, trashdir):
        return "TrashDir skipped because parent not sticky: %s" % trashdir

    def print_parse_path_error(self, offending_file):
        return "Parse Error: %s: Unable to parse Path." % offending_file


class Event:
    pass


class Error(Event):
    def __init__(self, error):
        self.error = error


class Output(Event):
    def __init__(self, message):
        self.message = message


def format_line(attribute, original_location):
    return "%s %s" % (attribute, original_location)


def format_line2(attribute, original_location, original_file):
    return "%s %s -> %s" % (attribute, original_location, original_file)
