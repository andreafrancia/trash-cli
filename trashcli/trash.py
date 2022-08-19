# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import

import datetime
import pwd

version = '0.22.8.19'

import os
import logging

logger=logging.getLogger('trashcli.trash')
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

# Error codes (from os on *nix, hard coded for Windows):
EX_OK    = getattr(os, 'EX_OK'   ,  0)
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


def volume_trash_dir1(volume, getuid):
    path = os.path.join(volume, '.Trash/%s' % getuid())
    yield path, volume


def volume_trash_dir2(volume, getuid):
    path = os.path.join(volume, ".Trash-%s" % getuid())
    yield path, volume


class MyEnum(str):
    def __repr__(self):
        return str(self)


trash_dir_found = MyEnum('trash_dir_found')
trash_dir_skipped_because_parent_not_sticky = \
    MyEnum('trash_dir_skipped_because_parent_not_sticky')
trash_dir_skipped_because_parent_is_symlink = \
    MyEnum('trash_dir_skipped_because_parent_is_symlink')


class UserInfo:
    def __init__(self, home_trash_dir_paths, uid):
        self.home_trash_dir_paths = home_trash_dir_paths
        self.uid = uid


class UserInfoProvider:
    def __init__(self, environ, getuid):
        self.environ = environ
        self.getuid = getuid

    def get_user_info(self):
        return [UserInfo(home_trash_dir_path_from_env(self.environ),
                         self.getuid())]


class AllUsersInfoProvider:
    def get_user_info(self):
        for user in pwd.getpwall():
            yield UserInfo([home_trash_dir_path_from_home(user.pw_dir)],
                           user.pw_uid)

class DirChecker:
    def is_dir(self, path):
        return os.path.isdir(path)

class TrashDirsScanner:
    def __init__(self,
                 user_info_provider,
                 volumes_listing,
                 top_trash_dir_rules,
                 dir_checker):
        self.user_info_provider = user_info_provider
        self.volumes_listing = volumes_listing
        self.top_trash_dir_rules = top_trash_dir_rules
        self.dir_checker = dir_checker


    def scan_trash_dirs(self, environ):
        for user_info in self.user_info_provider.get_user_info():
            for path in user_info.home_trash_dir_paths:
                yield trash_dir_found, (path, '/')
            for volume in self.volumes_listing.list_volumes(environ):
                top_trash_dir_path = os.path.join(volume, '.Trash', str(user_info.uid))
                result = self.top_trash_dir_rules.valid_to_be_read(top_trash_dir_path)
                if result == top_trash_dir_valid:
                    yield trash_dir_found, (top_trash_dir_path, volume)
                elif result == top_trash_dir_invalid_because_not_sticky:
                    yield trash_dir_skipped_because_parent_not_sticky, (top_trash_dir_path,)
                elif result == top_trash_dir_invalid_because_parent_is_symlink:
                    yield trash_dir_skipped_because_parent_is_symlink, (top_trash_dir_path,)
                alt_top_trash_dir = os.path.join(volume, '.Trash-%s' % user_info.uid)
                if self.dir_checker.is_dir(alt_top_trash_dir):
                    yield trash_dir_found, (alt_top_trash_dir, volume)


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
        self.println("Report bugs to https://github.com/andreafrancia/trash-cli/issues")

    def println(self, line):
        println(self.out, line)

def println(out, line):
    out.write(line + '\n')

class PrintHelp:
    def __init__(self, description, out):
        self.description  = description
        self.printer      = HelpPrinter(out)

    def my_print_help(self, program_name):
        self.description(program_name, self.printer)


def print_version(out, program_name, version):
    println(out, "%s %s" % (program_name, version))


top_trash_dir_does_not_exist = MyEnum('top_trash_dir_does_not_exist')
top_trash_dir_invalid_because_not_sticky = \
    MyEnum('top_trash_dir_invalid_because_not_sticky')
top_trash_dir_invalid_because_parent_is_symlink = \
    MyEnum('top_trash_dir_invalid_because_parent_is_symlink')
top_trash_dir_valid = MyEnum('top_trash_dir_valid')


class TopTrashDirRules:
    def __init__(self, fs):
        self.fs = fs

    def valid_to_be_read(self, path):
        parent_trashdir = os.path.dirname(path)
        if not self.fs.exists(path):
            return top_trash_dir_does_not_exist
        if not self.fs.is_sticky_dir(parent_trashdir):
            return top_trash_dir_invalid_because_not_sticky
        if self.fs.is_symlink(parent_trashdir):
            return top_trash_dir_invalid_because_parent_is_symlink
        else:
            return top_trash_dir_valid


class TrashDirReader:

    def __init__(self, file_reader):
        self.file_reader = file_reader

    def list_orphans(self, path):
        info_dir = os.path.join(path, 'info')
        files_dir = os.path.join(path, 'files')
        for entry in self.file_reader.entries_if_dir_exists(files_dir):
            trashinfo_path = os.path.join(info_dir, entry + '.trashinfo')
            file_path = os.path.join(files_dir, entry)
            if not self.file_reader.exists(trashinfo_path):
                yield file_path

    def list_trashinfo(self, path):
        info_dir = os.path.join(path, 'info')
        for entry in self.file_reader.entries_if_dir_exists(info_dir):
            if entry.endswith('.trashinfo'):
                yield os.path.join(info_dir, entry)


class ParseError(ValueError): pass


def maybe_parse_deletion_date(contents):
    result = Basket(unknown_date)
    parser = ParseTrashInfo(
            on_deletion_date = lambda date: result.collect(date),
            on_invalid_date = lambda: result.collect(unknown_date)
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
                 on_deletion_date = do_nothing,
                 on_invalid_date = do_nothing,
                 on_path = do_nothing):
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
                path=unquote(line[len('Path='):])
                self.found_path(path)

class Basket:
    def __init__(self, initial_value = None):
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
    def __init__(self, real_now, environ):
        self.real_now = real_now
        self.environ = environ

    def get_now_value(self, errors):
        if 'TRASH_DATE' in self.environ:
            try:
                return datetime.datetime.strptime(self.environ['TRASH_DATE'],
                                                  "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors.print_error('invalid TRASH_DATE: %s' %
                                   self.environ['TRASH_DATE'])
                return self.real_now()
        return self.real_now()
