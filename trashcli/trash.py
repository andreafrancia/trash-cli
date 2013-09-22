# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import

version='0.12.10.3~'

import os
import logging
from .fstab import Fstab

logger=logging.getLogger('trashcli.trash')
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

# Error codes (from os on *nix, hard coded for Windows):
EX_OK    = getattr(os, 'EX_OK'   ,  0)
EX_USAGE = getattr(os, 'EX_USAGE', 64)
EX_IOERR = getattr(os, 'EX_IOERR', 74)

from .fs import list_files_in_dir
import os
from .fs import remove_file
from .fs import move, mkdirs

class TrashDirectory:
    def __init__(self, path, volume):
        self.path      = os.path.normpath(path)
        self.volume    = volume
        self.logger    = logger
        self.info_dir  = os.path.join(self.path, 'info')
        self.files_dir = os.path.join(self.path, 'files')
        def warn_non_trashinfo():
            self.logger.warning("Non .trashinfo file in info dir")
        self.on_non_trashinfo_found = warn_non_trashinfo

    def trashed_files(self) :
        # Only used by trash-restore
        for info_file in self.all_info_files():
            try:
                yield self._create_trashed_file_from_info_file(info_file)
            except ValueError:
                self.logger.warning("Non parsable trashinfo file: %s" % info_file)
            except IOError as e:
                self.logger.warning(str(e))

    def all_info_files(self) :
        'Returns a generator of "Path"s'
        try :
            for info_file in list_files_in_dir(self.info_dir):
                if not os.path.basename(info_file).endswith('.trashinfo') :
                    self.on_non_trashinfo_found()
                else :
                    yield info_file
        except OSError: # when directory does not exist
            pass

    def _create_trashed_file_from_info_file(self, trashinfo_file_path):

        trash_info2 = LazyTrashInfoParser(
                lambda:contents_of(trashinfo_file_path), self.volume)

        original_location = trash_info2.original_location()
        deletion_date     = trash_info2.deletion_date()
        backup_file_path  = backup_file_path_from(trashinfo_file_path)

        return TrashedFile(original_location, deletion_date,
                trashinfo_file_path, backup_file_path, self)

def backup_file_path_from(trashinfo_file_path):
    trashinfo_basename = os.path.basename(trashinfo_file_path)
    backupfile_basename = trashinfo_basename[:-len('.trashinfo')]
    info_dir = os.path.dirname(trashinfo_file_path)
    trash_dir = os.path.dirname(info_dir)
    files_dir = os.path.join(trash_dir, 'files')
    return os.path.join(files_dir, backupfile_basename)

class HomeTrashCan:
    def __init__(self, environ):
        self.environ = environ
    def path_to(self, out):
        if 'XDG_DATA_HOME' in self.environ:
            out('%(XDG_DATA_HOME)s/Trash' % self.environ)
        elif 'HOME' in self.environ:
            out('%(HOME)s/.local/share/Trash' % self.environ)

class TrashDirectories:
    def __init__(self, volume_of, getuid, mount_points, environ):
        self.home_trashcan = HomeTrashCan(environ)
        self.volume_of = volume_of
        self.getuid = getuid
        self.mount_points = mount_points
    def all_trashed_files(self):
        for trash_dir in self.all_trash_directories():
            for trashedfile in trash_dir.trashed_files():
                yield trashedfile
    def all_trash_directories(self):
        collected = []
        def add_trash_dir(path, volume):
            collected.append(TrashDirectory(path, volume))

        self.home_trash_dir(add_trash_dir)
        for volume in self.mount_points:
            self.volume_trash_dir1(volume, add_trash_dir)
            self.volume_trash_dir2(volume, add_trash_dir)

        return collected
    def home_trash_dir(self, out) :
        self.home_trashcan.path_to(lambda path:
                out(path, self.volume_of(path)))
    def volume_trash_dir1(self, volume, out):
        out(
            path   = os.path.join(volume, '.Trash/%s' % self.getuid()),
            volume = volume)
    def volume_trash_dir2(self, volume, out):
        out(
            path   = os.path.join(volume, ".Trash-%s" % self.getuid()),
            volume = volume)

class TrashedFile:
    """
    Represent a trashed file.
    Each trashed file is persisted in two files:
     - $trash_dir/info/$id.trashinfo
     - $trash_dir/files/$id

    Properties:
     - path : the original path from where the file has been trashed
     - deletion_date : the time when the file has been trashed (instance of
                       datetime)
     - info_file : the file that contains information (instance of Path)
     - actual_path : the path where the trashed file has been placed after the
                     trash opeartion (instance of Path)
     - trash_directory :
    """
    def __init__(self, path, deletion_date, info_file, actual_path,
            trash_directory):
        self.path = path
        self.deletion_date = deletion_date
        self.info_file = info_file
        self.actual_path = actual_path
        self.trash_directory = trash_directory
        self.original_file = actual_path

    def restore(self, dest=None) :
        if dest is not None:
            raise NotImplementedError("not yet supported")
        if os.path.exists(self.path):
            raise IOError('Refusing to overwrite existing file "%s".' % os.path.basename(self.path))
        else:
            parent = os.path.dirname(self.path)
            mkdirs(parent)

        move(self.original_file, self.path)
        remove_file(self.info_file)

def getcwd_as_realpath(): return os.path.realpath(os.curdir)

import sys
class RestoreCmd:
    def __init__(self, stdout, stderr, environ, exit, input,
                 curdir = getcwd_as_realpath, version = version):
        self.out      = stdout
        self.err      = stderr
        self.exit     = exit
        self.input    = input
        fstab = Fstab()
        self.trashcan = TrashDirectories(
                volume_of     = fstab.volume_of,
                getuid        = os.getuid,
                mount_points  = fstab.mount_points(),
                environ       = environ)
        self.curdir   = curdir
        self.version = version
    def run(self, args = sys.argv):
        if '--version' in args[1:]:
            command = os.path.basename(args[0])
            self.println('%s %s' %(command, self.version))
            return

        trashed_files = []
        self.for_all_trashed_file_in_dir(trashed_files.append, self.curdir())

        if not trashed_files:
            self.report_no_files_found()
        else :
            for i, trashedfile in enumerate(trashed_files):
                self.println("%4d %s %s" % (i, trashedfile.deletion_date, trashedfile.path))
            index=self.input("What file to restore [0..%d]: " % (len(trashed_files)-1))
            if index == "" :
                self.println("Exiting")
            else :
                index = int(index)
                try:
                    trashed_files[index].restore()
                except IOError as e:
                    self.printerr(e)
                    self.exit(1)
    def for_all_trashed_file_in_dir(self, action, dir):
        def is_trashed_from_curdir(trashedfile):
            return trashedfile.path.startswith(dir + os.path.sep)
        for trashedfile in filter(is_trashed_from_curdir,
                                  self.trashcan.all_trashed_files()) :
            action(trashedfile)
    def report_no_files_found(self):
        self.println("No files trashed from current dir ('%s')" % self.curdir())
    def println(self, line):
        self.out.write(line + '\n')
    def printerr(self, msg):
        self.err.write('%s\n' % msg)

from .fs import FileSystemReader, contents_of, FileRemover

class ListCmd:
    def __init__(self, out, err, environ, list_volumes, getuid,
                 file_reader   = FileSystemReader(),
                 version       = version):

        self.output      = self.Output(out, err)
        self.err         = self.output.err
        self.contents_of = file_reader.contents_of
        self.version     = version
        top_trashdir_rules = TopTrashDirRules(file_reader)
        self.trashdirs = TrashDirs(environ, getuid,
                                   list_volumes = list_volumes,
                                   top_trashdir_rules=top_trashdir_rules)
        self.harvester = Harvester(file_reader)

    def run(self, *argv):
        parse=Parser()
        parse.on_help(PrintHelp(self.description, self.output.println))
        parse.on_version(PrintVersion(self.output.println, self.version))
        parse.as_default(self.list_trash)
        parse(argv)
    def list_trash(self):
        self.harvester.on_volume = self.output.set_volume_path
        self.harvester.on_trashinfo_found = self._print_trashinfo

        self.trashdirs.on_trashdir_skipped_because_parent_not_sticky = self.output.top_trashdir_skipped_because_parent_not_sticky
        self.trashdirs.on_trashdir_skipped_because_parent_is_symlink = self.output.top_trashdir_skipped_because_parent_is_symlink
        self.trashdirs.on_trash_dir_found = self.harvester._analize_trash_directory

        self.trashdirs.list_trashdirs()
    def _print_trashinfo(self, path):
        try:
            contents = self.contents_of(path)
        except IOError as e :
            self.output.print_read_error(e)
        else:
            deletion_date = parse_deletion_date(contents) or unknown_date()
            try:
                path = parse_path(contents)
            except ParseError:
                self.output.print_parse_path_error(path)
            else:
                self.output.print_entry(deletion_date, path)
    def description(self, program_name, printer):
        printer.usage('Usage: %s [OPTIONS...]' % program_name)
        printer.summary('List trashed files')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()
    class Output:
        def __init__(self, out, err):
            self.out = out
            self.err = err
        def println(self, line):
            self.out.write(line+'\n')
        def error(self, line):
            self.err.write(line+'\n')
        def print_read_error(self, error):
            self.error(str(error))
        def print_parse_path_error(self, offending_file):
            self.error("Parse Error: %s: Unable to parse Path." % (offending_file))
        def top_trashdir_skipped_because_parent_not_sticky(self, trashdir):
            self.error("TrashDir skipped because parent not sticky: %s"
                    % trashdir)
        def top_trashdir_skipped_because_parent_is_symlink(self, trashdir):
            self.error("TrashDir skipped because parent is symlink: %s"
                    % trashdir)
        def set_volume_path(self, volume_path):
            self.volume_path = volume_path
        def print_entry(self, maybe_deletion_date, relative_location):
            import os
            original_location = os.path.join(self.volume_path, relative_location)
            self.println("%s %s" %(maybe_deletion_date, original_location))

def do_nothing(*argv, **argvk): pass
class Parser:
    def __init__(self):
        self.default_action = do_nothing
        self.argument_action = do_nothing
        self.short_options = ''
        self.long_options = []
        self.actions = dict()
        self._on_invalid_option = do_nothing

    def __call__(self, argv):
        program_name = argv[0]
        from getopt import getopt, GetoptError

        try:
            options, arguments = getopt(argv[1:],
                                        self.short_options,
                                        self.long_options)
        except GetoptError, e:
            invalid_option = e.opt
            self._on_invalid_option(program_name, invalid_option)
        else:
            for option, value in options:
                if option in self.actions:
                    self.actions[option](program_name)
                    return
            for argument in arguments:
                self.argument_action(argument)
            self.default_action()

    def on_invalid_option(self, action):
        self._on_invalid_option = action

    def on_help(self, action):
        self.add_option('help', action, 'h')

    def on_version(self, action):
        self.add_option('version', action)

    def add_option(self, long_option, action, short_aliases=''):
        self.long_options.append(long_option)
        self.actions['--' + long_option] = action
        for short_alias in short_aliases:
            self.add_short_option(short_alias, action)

    def add_short_option(self, short_option, action):
        self.short_options += short_option
        self.actions['-' + short_option] = action

    def on_argument(self, argument_action):
        self.argument_action = argument_action
    def as_default(self, default_action):
        self.default_action = default_action

class CleanableTrashcan:
    def __init__(self, file_remover):
        self._file_remover = file_remover
    def delete_orphan(self, path_to_backup_copy):
        self._file_remover.remove_file(path_to_backup_copy)
    def delete_trashinfo_and_backup_copy(self, trashinfo_path):
        backup_copy = self._path_of_backup_copy(trashinfo_path)
        self._file_remover.remove_file_if_exists(backup_copy)
        self._file_remover.remove_file(trashinfo_path)
    def _path_of_backup_copy(self, path_to_trashinfo):
        from os.path import dirname as parent_of, join, basename
        trash_dir = parent_of(parent_of(path_to_trashinfo))
        return join(trash_dir, 'files', basename(path_to_trashinfo)[:-len('.trashinfo')])

class ExpiryDate:
    def __init__(self, contents_of, now, trashcan):
        self._contents_of  = contents_of
        self._now          = now
        self._maybe_delete = self._delete_unconditionally
        self._trashcan = trashcan
    def set_max_age_in_days(self, arg):
        self.max_age_in_days = int(arg)
        self._maybe_delete = self._delete_according_date
    def delete_if_expired(self, trashinfo_path):
        self._maybe_delete(trashinfo_path)
    def _delete_according_date(self, trashinfo_path):
        contents = self._contents_of(trashinfo_path)
        ParseTrashInfo(
            on_deletion_date=IfDate(
                OlderThan(self.max_age_in_days, self._now),
                lambda: self._delete_unconditionally(trashinfo_path)
            ),
        )(contents)
    def _delete_unconditionally(self, trashinfo_path):
        self._trashcan.delete_trashinfo_and_backup_copy(trashinfo_path)

class TrashDirs:
    def __init__(self, environ, getuid, list_volumes, top_trashdir_rules):
        self.getuid             = getuid
        self.mount_points       = list_volumes
        self.top_trashdir_rules = top_trashdir_rules
        self.home_trashcan      = HomeTrashCan(environ)
        # events
        self.on_trash_dir_found                            = lambda trashdir, volume: None
        self.on_trashdir_skipped_because_parent_not_sticky = lambda trashdir: None
        self.on_trashdir_skipped_because_parent_is_symlink = lambda trashdir: None
    def list_trashdirs(self):
        self.emit_home_trashcan()
        self._for_each_volume_trashcan()
    def emit_home_trashcan(self):
        def return_result_with_volume(trashcan_path):
            self.on_trash_dir_found(trashcan_path, '/')
        self.home_trashcan.path_to(return_result_with_volume)
    def _for_each_volume_trashcan(self):
        for volume in self.mount_points():
            self.emit_trashcans_for(volume)
    def emit_trashcans_for(self, volume):
        self.emit_trashcan_1_for(volume)
        self.emit_trashcan_2_for(volume)
    def emit_trashcan_1_for(self,volume):
        top_trashdir_path = os.path.join(volume, '.Trash/%s' % self.getuid())
        class IsValidOutput:
            def not_valid_parent_should_not_be_a_symlink(_):
                self.on_trashdir_skipped_because_parent_is_symlink(top_trashdir_path)
            def not_valid_parent_should_be_sticky(_):
                self.on_trashdir_skipped_because_parent_not_sticky(top_trashdir_path)
            def is_valid(_):
                self.on_trash_dir_found(top_trashdir_path, volume)
        self.top_trashdir_rules.valid_to_be_read(top_trashdir_path, IsValidOutput())
    def emit_trashcan_2_for(self, volume):
        alt_top_trashdir = os.path.join(volume, '.Trash-%s' % self.getuid())
        self.on_trash_dir_found(alt_top_trashdir, volume)

from datetime import datetime
class EmptyCmd:
    def __init__(self, out, err, environ, list_volumes,
                 now           = datetime.now,
                 file_reader   = FileSystemReader(),
                 getuid        = os.getuid,
                 file_remover  = FileRemover(),
                 version       = version):

        self.out          = out
        self.err          = err
        self.file_reader  = file_reader
        top_trashdir_rules = TopTrashDirRules(file_reader)
        self.trashdirs = TrashDirs(environ, getuid,
                                   list_volumes = list_volumes,
                                   top_trashdir_rules = top_trashdir_rules)
        self.harvester = Harvester(file_reader)
        self.version      = version
        self._cleaning    = CleanableTrashcan(file_remover)
        self._expiry_date = ExpiryDate(file_reader.contents_of, now,
                                       self._cleaning)

    def run(self, *argv):
        self.exit_code     = EX_OK

        parse = Parser()
        parse.on_help(PrintHelp(self.description, self.println))
        parse.on_version(PrintVersion(self.println, self.version))
        parse.on_argument(self._expiry_date.set_max_age_in_days)
        parse.as_default(self._empty_all_trashdirs)
        parse.on_invalid_option(self.report_invalid_option_usage)

        parse(argv)

        return self.exit_code

    def report_invalid_option_usage(self, program_name, option):
        self.err.write(
            "{program_name}: invalid option -- '{option}'\n".format(**locals()))
        self.exit_code |= EX_USAGE

    def description(self, program_name, printer):
        printer.usage('Usage: %s [days]' % program_name)
        printer.summary('Purge trashed files.')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()
    def _empty_all_trashdirs(self):
        self.harvester.on_trashinfo_found = self._expiry_date.delete_if_expired
        self.harvester.on_orphan_found = self._cleaning.delete_orphan
        self.trashdirs.on_trash_dir_found = self.harvester._analize_trash_directory
        self.trashdirs.list_trashdirs()
    def println(self, line):
        self.out.write(line + '\n')

class Harvester:
    def __init__(self, file_reader):
        self.file_reader = file_reader
        self.trashdir = TrashDir(self.file_reader)

        self.on_orphan_found                               = do_nothing
        self.on_trashinfo_found                            = do_nothing
        self.on_volume                                     = do_nothing
    def _analize_trash_directory(self, trash_dir_path, volume_path):
        self.on_volume(volume_path)
        self.trashdir.open(trash_dir_path, volume_path)
        self.trashdir.each_trashinfo(self.on_trashinfo_found)
        self.trashdir.each_orphan(self.on_orphan_found)

class IfDate:
    def __init__(self, date_criteria, then):
        self.date_criteria = date_criteria
        self.then          = then
    def __call__(self, date2):
        if self.date_criteria(date2):
            self.then()
class OlderThan:
    def __init__(self, days_ago, now):
        from datetime import timedelta
        self.limit_date = now() - timedelta(days=days_ago)
    def __call__(self, deletion_date):
        return deletion_date < self.limit_date

class PrintHelp:
    def __init__(self, description, println):
        class Printer:
            def __init__(self, println):
                self.println = println
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
                self.println("Report bugs to http://code.google.com/p/trash-cli/issues")
        self.description  = description
        self.printer      = Printer(println)

    def __call__(self, program_name):
        self.description(program_name, self.printer)

class PrintVersion:
    def __init__(self, println, version):
        self.println      = println
        self.version      = version
    def __call__(self, program_name):
        self.println("%s %s" % (program_name, self.version))

class TopTrashDirRules:
    def __init__(self, fs):
        self.fs = fs

    def valid_to_be_read(self, path, output):
        parent_trashdir = os.path.dirname(path)
        if not self.fs.exists(path):
            return
        if not self.fs.is_sticky_dir(parent_trashdir):
            output.not_valid_parent_should_be_sticky()
            return
        if self.fs.is_symlink(parent_trashdir):
            output.not_valid_parent_should_not_be_a_symlink()
            return
        else:
            output.is_valid()

class Dir:
    def __init__(self, path, entries_if_dir_exists):
        self.path                  = path
        self.entries_if_dir_exists = entries_if_dir_exists
    def entries(self):
        return self.entries_if_dir_exists(self.path)
    def full_path(self, entry):
        return os.path.join(self.path, entry)

class TrashDir:
    def __init__(self, file_reader):
        self.file_reader    = file_reader
    def open(self, path, volume_path):
        self.trash_dir_path = path
        self.volume_path    = volume_path
        self.files_dir      = Dir(self._files_dir(),
                                  self.file_reader.entries_if_dir_exists)
    def each_orphan(self, action):
        for entry in self.files_dir.entries():
            trashinfo_path = self._trashinfo_path_from_file(entry)
            file_path = self.files_dir.full_path(entry)
            if not self.file_reader.exists(trashinfo_path): action(file_path)
    def _entries_if_dir_exists(self, path):
        return self.file_reader.entries_if_dir_exists(path)

    def each_trashinfo(self, action):
        for entry in self._trashinfo_entries():
            action(os.path.join(self._info_dir(), entry))
    def _info_dir(self):
        return os.path.join(self.trash_dir_path, 'info')
    def _trashinfo_path_from_file(self, file_entry):
        return os.path.join(self._info_dir(), file_entry + '.trashinfo')
    def _files_dir(self):
        return os.path.join(self.trash_dir_path, 'files')
    def _trashinfo_entries(self, on_non_trashinfo=do_nothing):
        for entry in self._entries_if_dir_exists(self._info_dir()):
            if entry.endswith('.trashinfo'):
                yield entry
            else:
                on_non_trashinfo()

class ParseError(ValueError): pass

class LazyTrashInfoParser:
    def __init__(self, contents, volume_path):
        self.contents    = contents
        self.volume_path = volume_path
    def deletion_date(self):
        return parse_deletion_date(self.contents())
    def _path(self):
        return parse_path(self.contents())
    def original_location(self):
        return os.path.join(self.volume_path, self._path())

def maybe_parse_deletion_date(contents):
    result = Basket(unknown_date())
    ParseTrashInfo(
            on_deletion_date = lambda date: result.collect(date),
            on_invalid_date = lambda: result.collect(unknown_date())
    )(contents)
    return result.collected

def unknown_date():
    return '????-??-?? ??:??:??'

class ParseTrashInfo:
    def __init__(self,
                 on_deletion_date = do_nothing,
                 on_invalid_date = do_nothing,
                 on_path = do_nothing):
        self.found_deletion_date = on_deletion_date
        self.found_invalid_date = on_invalid_date
        self.found_path = on_path
    def __call__(self, contents):
        from datetime import datetime
        import urllib
        for line in contents.split('\n'):
            if line.startswith('DeletionDate='):
                try:
                    date = datetime.strptime(line, "DeletionDate=%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    self.found_invalid_date()
                else:
                    self.found_deletion_date(date)

            if line.startswith('Path='):
                path=urllib.unquote(line[len('Path='):])
                self.found_path(path)

class Basket:
    def __init__(self, initial_value = None):
        self.collected = initial_value
    def collect(self, value):
        self.collected = value
def parse_deletion_date(contents):
    result = Basket()
    ParseTrashInfo(on_deletion_date=result.collect)(contents)
    return result.collected

def parse_path(contents):
    import urllib
    for line in contents.split('\n'):
        if line.startswith('Path='):
            return urllib.unquote(line[len('Path='):])
    raise ParseError('Unable to parse Path')

