import os

from trashcli.py2compat import url_quote
from trashcli.trash import path_of_backup_copy


def parent_realpath(path):
    parent = os.path.dirname(path)
    return os.path.realpath(parent)


class TrashDirectoryForPut:
    def __init__(self, path, volume, fs, path_maker, info_dir):
        self.path = os.path.normpath(path)
        self.volume = volume
        self.fs = fs
        self.path_maker = path_maker
        self.info_dir = info_dir

    def trash2(self, path, now, program_name, verbose):
        path = os.path.normpath(path)

        original_location = self.path_for_trash_info_for_file(path)

        basename = os.path.basename(original_location)
        content = format_trashinfo(original_location, now())
        trash_info_file = self.info_dir.persist_trash_info(basename, content, program_name, verbose)

        where_to_store_trashed_file = path_of_backup_copy(trash_info_file)

        try:
            self.fs.move(path, where_to_store_trashed_file)
        except IOError as e:
            self.fs.remove_file(trash_info_file)
            raise e

    def path_for_trash_info_for_file(self, path):
        path_for_trash_info = OriginalLocation(parent_realpath,
                                               self.path_maker)
        return path_for_trash_info.for_file(path)


def format_trashinfo(original_location, deletion_date):
    content = ("[Trash Info]\n" +
               "Path=%s\n" % format_original_location(original_location) +
               "DeletionDate=%s\n" % format_date(deletion_date)).encode('utf-8')
    return content


def format_date(deletion_date):
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")


def format_original_location(original_location):
    return url_quote(original_location, '/')


class OriginalLocation:
    def __init__(self, parent_realpath, path_maker):
        self.parent_realpath = parent_realpath
        self.path_maker = path_maker

    def for_file(self, path):
        self.normalized_path = os.path.normpath(path)

        basename = os.path.basename(self.normalized_path)
        parent = self.parent_realpath(self.normalized_path)

        parent = self.path_maker.calc_parent_path(parent)

        return os.path.join(parent, basename)
