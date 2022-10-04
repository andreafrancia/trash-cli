# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import
import datetime
import logging
import os
import pwd


version = '0.22.10.4.4'

logger = logging.getLogger('trashcli.trash')
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

# Error codes (from os on *nix, hard coded for Windows):
EX_OK = getattr(os, 'EX_OK', 0)
EX_USAGE = getattr(os, 'EX_USAGE', 64)
EX_IOERR = getattr(os, 'EX_IOERR', 74)

try:
    my_input = raw_input  # Python 2
except NameError:
    my_input = input  # Python 3


def path_of_backup_copy(trashinfo_path):
    trash_dir = os.path.dirname(os.path.dirname(trashinfo_path))
    basename = os.path.basename(trashinfo_path)[:-len('.trashinfo')]
    return os.path.join(trash_dir, 'files', basename)


def home_trash_dir_path_from_env(environ):
    if 'XDG_DATA_HOME' in environ:
        return ['%(XDG_DATA_HOME)s/Trash' % environ]
    elif 'HOME' in environ:
        return ['%(HOME)s/.local/share/Trash' % environ]
    return []


def home_trash_dir_path_from_home(home_dir):
    return '%s/.local/share/Trash' % home_dir


def home_trash_dir(environ, volume_of):
    paths = home_trash_dir_path_from_env(environ)
    for path in paths:
        yield path, volume_of(path)


def volume_trash_dir1(volume, uid):
    path = os.path.join(volume, '.Trash/%s' % uid)
    yield path, volume


def volume_trash_dir2(volume, uid):
    path = os.path.join(volume, ".Trash-%s" % uid)
    yield path, volume


class UserInfo:
    def __init__(self, home_trash_dir_paths, uid):
        self.home_trash_dir_paths = home_trash_dir_paths
        self.uid = uid


class UserInfoProvider:
    @staticmethod
    def get_user_info(environ, uid):
        return [UserInfo(home_trash_dir_path_from_env(environ), uid)]


class AllUsersInfoProvider:
    @staticmethod
    def get_user_info(_environ, _uid):
        for user in pwd.getpwall():
            yield UserInfo([home_trash_dir_path_from_home(user.pw_dir)],
                           user.pw_uid)


class DirChecker:
    @staticmethod
    def is_dir(path):
        return os.path.isdir(path)


class HelpPrinter:
    def __init__(self, out):
        self.out = out

    def usage(self, usage):
        self.println(usage)
        self.println('')

    def summary(self, summary):
        self.println(summary)
        self.println('')

    def options(self, *line_describing_option):
        self.println('Options:')
        for line in line_describing_option:
            self.println(line)
        self.println('')

    def bug_reporting(self):
        self.println(
            "Report bugs to https://github.com/andreafrancia/trash-cli/issues")

    def println(self, line):
        println(self.out, line)


def println(out, line):
    out.write(line + '\n')


class PrintHelp:
    def __init__(self, description, out):
        self.description = description
        self.printer = HelpPrinter(out)

    def my_print_help(self, program_name):
        self.description(program_name, self.printer)


def print_version(out, program_name, version):
    println(out, "%s %s" % (program_name, version))


class DirReader:
    def entries_if_dir_exists(self, path):  # type: (str) -> list[str]
        raise NotImplementedError()

    def exists(self, path):  # type: (str) -> bool
        raise NotImplementedError()


class TrashDirReader:

    def __init__(self, dir_reader):  # type: (DirReader) -> None
        self.dir_reader = dir_reader

    def list_orphans(self, path):
        info_dir = os.path.join(path, 'info')
        files_dir = os.path.join(path, 'files')
        for entry in self.dir_reader.entries_if_dir_exists(files_dir):
            trashinfo_path = os.path.join(info_dir, entry + '.trashinfo')
            file_path = os.path.join(files_dir, entry)
            if not self.dir_reader.exists(trashinfo_path):
                yield file_path

    def list_trashinfo(self, path):
        info_dir = os.path.join(path, 'info')
        for entry in self.dir_reader.entries_if_dir_exists(info_dir):
            if entry.endswith('.trashinfo'):
                yield os.path.join(info_dir, entry)


class ParseError(ValueError): pass


def maybe_parse_deletion_date(contents):
    result = Basket(unknown_date)
    parser = ParseTrashInfo(
        on_deletion_date=lambda date: result.collect(date),
        on_invalid_date=lambda: result.collect(unknown_date)
    )
    parser.parse_trashinfo(contents)
    return result.collected


unknown_date = '????-??-?? ??:??:??'

try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote


def do_nothing(*argv, **argvk): pass


class ParseTrashInfo:
    def __init__(self,
                 on_deletion_date=do_nothing,
                 on_invalid_date=do_nothing,
                 on_path=do_nothing):
        self.found_deletion_date = on_deletion_date
        self.found_invalid_date = on_invalid_date
        self.found_path = on_path

    def parse_trashinfo(self, contents):
        found_deletion_date = False
        for line in contents.split('\n'):
            if not found_deletion_date and line.startswith('DeletionDate='):
                found_deletion_date = True
                try:
                    date = datetime.datetime.strptime(
                        line, "DeletionDate=%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    self.found_invalid_date()
                else:
                    self.found_deletion_date(date)

            if line.startswith('Path='):
                path = unquote(line[len('Path='):])
                self.found_path(path)


class Basket:
    def __init__(self, initial_value=None):
        self.collected = initial_value

    def collect(self, value):
        self.collected = value


def parse_deletion_date(contents):
    result = Basket()
    parser = ParseTrashInfo(on_deletion_date=result.collect)
    parser.parse_trashinfo(contents)
    return result.collected


def parse_path(contents):
    for line in contents.split('\n'):
        if line.startswith('Path='):
            return unquote(line[len('Path='):])
    raise ParseError('Unable to parse Path')


def parse_original_location(contents, volume_path):
    path = parse_path(contents)
    return os.path.join(volume_path, path)


class Clock:
    def __init__(self, real_now, errors):
        self.real_now = real_now
        self.errors = errors

    def get_now_value(self, environ):
        if 'TRASH_DATE' in environ:
            try:
                return datetime.datetime.strptime(environ['TRASH_DATE'],
                                                  "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                self.errors.print_error('invalid TRASH_DATE: %s' %
                                        environ['TRASH_DATE'])
                return self.real_now()
        return self.real_now()
