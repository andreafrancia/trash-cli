# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy
from __future__ import absolute_import

version='0.12.9.14'

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
class TrashDirectory:
    def __init__(self, path, volume):
        self.path   = os.path.normpath(path)
        self.volume = volume
        class all_is_ok_checker:
            def valid_to_be_written(self, a, b): pass
            def check(self, a):pass
        self.checker = all_is_ok_checker()
        # events
        def warn_non_trashinfo():
            self.logger.warning("Non .trashinfo file in info dir")
        self.on_non_trashinfo_found = warn_non_trashinfo
        self.logger = logger

    def __str__(self) :
        return self.name()

    def __repr__(self):
        return 'TrashDirectory(%s,%s)' % (repr(self.path), repr(self.volume))

    def name(self):
        import re
        import posixpath
        result=self.path
        try:
            home_dir=os.environ['HOME']
            home_dir = posixpath.normpath(home_dir)
            if home_dir != '':
                result=re.sub('^'+ re.escape(home_dir)+os.path.sep, '~' + os.path.sep,result)
        except KeyError:
            pass
        return result

    def store_absolute_paths(self):
        self.path_for_trash_info = PathForTrashInfo()
        self.path_for_trash_info.make_absolutes_paths()

    def store_relative_paths(self):
        self.path_for_trash_info = PathForTrashInfo()
        self.path_for_trash_info.make_paths_relatives_to(self.volume)

    def trash(self, path):
        path = os.path.normpath(path)

        from datetime import datetime
        trash_info_path = self.path_for_trash_info.for_file(path)
        trash_info = TrashInfo(trash_info_path, datetime.now())

        basename = os.path.basename(trash_info.path)
        trashinfo_file_content = trash_info.render()
        (trash_info_file, trash_info_id) = self.persist_trash_info(basename,
                                                                   trashinfo_file_content)

        trashed_file = self._create_trashed_file(trash_info_id,
                                                 os.path.abspath(path),
                                                 trash_info.deletion_date)

        self.ensure_files_dir_exists()

        try :
            move(path, trashed_file.actual_path)
        except IOError as e :
            remove_file(trash_info_file)
            raise e

        return trashed_file

    def ensure_files_dir_exists(self):
        if not os.path.exists(self.files_dir) :
            mkdirs_using_mode(self.files_dir, 0700)

    @property
    def info_dir(self):
        """
        The $trash_dir/info dir that contains the .trashinfo files
        as filesystem.Path.
        """
        result = os.path.join(self.path, 'info')
        return result

    @property
    def files_dir(self):
        """
        The directory where original file where stored.
        A Path instance.
        """
        result = os.path.join(self.path, 'files')
        return result

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

    def trashed_files(self) :
        # Only used by restore-trash
        for info_file in self.all_info_files():
            try:
                yield self._create_trashed_file_from_info_file(info_file)
            except ValueError:
                self.logger.warning("Non parsable trashinfo file: %s" % info_file)
            except IOError as e:
                self.logger.warning(str(e))

    def _create_trashed_file_from_info_file(self, info_file):
        trash_id = self.calc_id(info_file)

        trash_info2   = LazyTrashInfoParser(lambda:contents_of(info_file),
                                            self.volume)
        path          = trash_info2.original_location()
        deletion_date = trash_info2.deletion_date()

        trashed_file = self._create_trashed_file(
                trash_id, path, deletion_date)

        return trashed_file

    def _create_trashed_file(self, trash_id, path, deletion_date):
        actual_path = self._calc_path_for_actual_file(trash_id)
        info_file   = self._calc_path_for_info_file(trash_id)

        return TrashedFile(path,
                           deletion_date,
                           info_file,
                           actual_path,
                           self)

    @staticmethod
    def calc_id(trash_info_file):
        return os.path.basename(trash_info_file)[:-len('.trashinfo')]

    def _calc_path_for_actual_file(self, trash_id) :
        return os.path.join(self.files_dir, trash_id)

    def _calc_path_for_info_file(self, trash_id) :
        return os.path.join(self.info_dir, '%s.trashinfo' % trash_id)

    """
    Create a .trashinfo file in the $trash/info directory.
    returns the created TrashInfoFile.
    """
    def persist_trash_info(self,basename,content) :

        mkdirs_using_mode(self.info_dir, 0700)
        os.chmod(self.info_dir,0700)

        # write trash info
        index = 0
        while True :
            if index == 0 :
                suffix = ""
            elif index < 100:
                suffix = "_%d" % index
            else :
                import random
                suffix = "_%d" % random.randint(0, 65535)

            base_id = basename
            trash_id = base_id + suffix
            trash_info_basename = trash_id+".trashinfo"

            dest = os.path.join(self.info_dir, trash_info_basename)
            try :
                handle = os.open(dest,
                                 os.O_RDWR | os.O_CREAT | os.O_EXCL,
                                 0600)
                os.write(handle, content)
                os.close(handle)
                self.logger.debug(".trashinfo created as %s." % dest)
                return (dest, trash_id)
            except OSError:
                self.logger.debug("Attempt for creating %s failed." % dest)

            index += 1

        raise IOError()

class PathForTrashInfo:
    def make_paths_relatives_to(self, topdir):
        self.topdir = topdir

    def make_absolutes_paths(self):
        self.topdir = None

    def for_file(self, path):
        self.normalized_path = os.path.normpath(path)

        basename = os.path.basename(self.normalized_path)
        parent   = self._real_parent()

        if self.topdir != None:
            if (parent == self.topdir) or parent.startswith(self.topdir+os.path.sep) :
                parent = parent[len(self.topdir+os.path.sep):]

        result   = os.path.join(parent, basename)
        return result

    def _real_parent(self):
        parent   = os.path.dirname(self.normalized_path)
        return os.path.realpath(parent)

class NullObject:
    def __getattr__(self, name):
        return lambda *argl,**args:None

class HomeTrashCan:
    def __init__(self, environ):
        self.environ = environ
    def path_to(self, out):
        if 'XDG_DATA_HOME' in self.environ:
            out('%(XDG_DATA_HOME)s/Trash' % self.environ)
        elif 'HOME' in self.environ:
            out('%(HOME)s/.local/share/Trash' % self.environ)

class GlobalTrashCan:
    """
    Represent the TrashCan that contains all trashed files.
    This class is the facade used by all trashcli commands
    """

    class NullReporter:
        def __getattr__(self,name):
            return lambda *argl,**args:None
    from datetime import datetime
    def __init__(self, home_trashcan,
                       reporter = NullReporter(),
                       getuid   = os.getuid,
                       fstab    = Fstab(),
                       now      = datetime.now):
        self.getuid        = getuid
        self.reporter      = reporter
        self.fstab         = fstab
        self.now           = now
        self.home_trashcan = home_trashcan

    def trashed_files(self):
        """Return a generator of all TrashedFile(s)."""
        for trash_dir in self._trash_directories():
            for trashedfile in trash_dir.trashed_files():
                yield trashedfile

    def trash(self, file) :
        """
        Trash a file in the appropriate trash directory.
        If the file belong to the same volume of the trash home directory it
        will be trashed in the home trash directory.
        Otherwise it will be trashed in one of the relevant volume trash
        directories.

        Each volume can have two trash directories, they are
            - $volume/.Trash/$uid
            - $volume/.Trash-$uid

        Firstly the software attempt to trash the file in the first directory
        then try to trash in the second trash directory.
        """

        if self._should_skipped_by_specs(file):
            self.reporter.unable_to_trash_dot_entries(file)
            return

        for trash_dir in self._possible_trash_directories_for(file):

            try:
                class ValidationOutput:
                    def not_valid_should_be_a_dir(_):
                        raise TopDirNotPresent("topdir should be a directory: %s"
                                            % trash_dir.path)
                    def not_valid_parent_should_not_be_a_symlink(_):
                        raise TopDirIsSymLink("topdir can't be a symbolic link: %s"
                                            % trash_dir.path)
                    def not_valid_parent_should_be_sticky(_):
                        raise TopDirWithoutStickyBit("topdir should have the sticky bit: %s"
                                            % trash_dir.path)
                    def is_valid(self):
                        pass
                output = ValidationOutput()
                class FileSystem:
                    def isdir(self, path):
                        return os.path.isdir(path)
                    def islink(self, path):
                        return os.path.islink(path)
                    def has_sticky_bit(self, path):
                        return has_sticky_bit(path)
                trash_dir.checker.fs = FileSystem()
                trash_dir.checker.valid_to_be_written(trash_dir.path, output)
            except TopDirIsSymLink:
                self.reporter.found_unsercure_trash_dir_symlink(
                        os.path.dirname(trash_dir.path))
            except TopDirNotPresent:
                self.reporter.found_unusable_trash_dir_not_a_dir(
                        os.path.dirname(trash_dir.path))
            except TopDirWithoutStickyBit:
                self.reporter.found_unsecure_trash_dir_unsticky(
                        os.path.dirname(trash_dir.path))

            if self._file_could_be_trashed_in(file, trash_dir.path):
                try:
                    trashed_file = trash_dir.trash(file)
                    self.reporter.file_has_been_trashed_in_as(
                          file,
                          trashed_file.trash_directory.name(),
                          trashed_file.original_file)
                    return

                except (IOError, OSError), error:
                    self.reporter.unable_to_trash_file_in_because(
                            file, trash_dir.name(), str(error))

        self.reporter.unable_to_trash_file(file)

    def _should_skipped_by_specs(self, file):
        basename = os.path.basename(file)
        return (basename == ".") or (basename == "..")

    def volume_of(self, path):
        return self.fstab.volume_of(path)

    def _file_could_be_trashed_in(self,file_to_be_trashed,trash_dir_path):
        return self.volume_of(trash_dir_path) == self.volume_of_parent(file_to_be_trashed)

    def _trash_directories(self) :
        """Return a generator of all TrashDirectories in the filesystem"""
        for td in self._home_trash_dir():
            yield td
        for mount_point in self.fstab.mount_points():
            volume = mount_point
            yield self._volume_trash_dir1(volume)
            yield self._volume_trash_dir2(volume)
    def _possible_trash_directories_for(self, file):
        for td in self._home_trash_dir():
            yield td
        for td in self._trash_directories_for_volume(self.volume_of_parent(file)):
            yield td
    def volume_of_parent(self, file):
        return self.volume_of(parent_of(file))
    def _trash_directories_for_volume(self, volume):
        yield self._volume_trash_dir1(volume)
        yield self._volume_trash_dir2(volume)
    def _home_trash_dir(self) :
        paths = []
        self.home_trashcan.path_to(paths.append)

        result = []
        for trash_dir_path in paths:
            trash_dir = TrashDirectory(trash_dir_path, self.volume_of(trash_dir_path))
            trash_dir.volume_of = self.volume_of
            trash_dir.store_absolute_paths()
            result.append(trash_dir)
        return result
    def _volume_trash_dir1(self, volume):
        """
        Return the method (1) volume trash dir ($topdir/.Trash/$uid).
        """
        uid = self.getuid()
        trash_directory_path = os.path.join(volume, '.Trash', str(uid))
        trash_dir = TrashDirectory(trash_directory_path,volume)
        trash_dir.volume_of = self.volume_of
        trash_dir.store_relative_paths()
        trash_dir.checker = TopTrashDirRules(None)
        return trash_dir
    def _volume_trash_dir2(self, volume) :
        """
        Return the method (2) volume trash dir ($topdir/.Trash-$uid).
        """
        uid = self.getuid()
        dirname=".Trash-%s" % str(uid)
        trash_directory_path = os.path.join(volume, dirname)
        trash_dir = TrashDirectory(trash_directory_path,volume)
        trash_dir.volume_of = self.volume_of
        trash_dir.store_relative_paths()
        return trash_dir

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
    def __init__(self,
                 path,
                 deletion_date,
                 info_file,
                 actual_path,
                 trash_directory) :

        if not os.path.isabs(path):
            raise ValueError("Absolute path required.")

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

class TrashInfo:
    def __init__(self, path, deletion_date):
        assert isinstance(deletion_date, datetime)
        self.path = path
        self.deletion_date = deletion_date

    def render(self) :
        import urllib
        result = "[Trash Info]\n"
        result += "Path=" + urllib.quote(self.path,'/') + "\n"
        result += "DeletionDate=" + self._format_date(self.deletion_date) + "\n"
        return result

    @staticmethod
    def _format_date(deletion_date):
        return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def parse(data):
        path = parse_path(data)
        deletion_date = parse_deletion_date(data)
        return TrashInfo(path, deletion_date)

import os
from .fs import remove_file, has_sticky_bit
from .fs import move, mkdirs, mkdirs_using_mode, parent_of

def getcwd_as_realpath(): return os.path.realpath(os.curdir)

import sys
class RestoreCmd:
    def __init__(self, stdout, stderr, environ, exit, input,
                 curdir = getcwd_as_realpath, version = version):
        self.out      = stdout
        self.err      = stderr
        self.exit     = exit
        self.input    = input
        self.trashcan = GlobalTrashCan(
                home_trashcan = HomeTrashCan(environ))
        self.curdir   = curdir
        self.version = version
    def run(self, args=sys.argv):
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
                                  self.trashcan.trashed_files()) :
            action(trashedfile)
    def report_no_files_found(self):
        self.println("No files trashed from current dir ('%s')" % self.curdir())
    def println(self, line):
        self.out.write(line + '\n')
    def printerr(self, msg):
        self.err.write('%s\n' % msg)

from optparse import IndentedHelpFormatter
class NoWrapFormatter(IndentedHelpFormatter) :
    def _format_text(self, text) :
        "[Does not] format a text, return the text as it is."
        return text

class TrashPutCmd:
    def __init__(self, stdout, stderr, environ = os.environ, fstab = Fstab()):
        self.stdout  = stdout
        self.stderr  = stderr
        self.environ = environ
        self.fstab   = fstab

    def run(self, argv):
        parser = self.get_option_parser(os.path.basename(argv[0]))
        (options, args) = parser.parse_args(argv[1:])

        if len(args) <= 0:
            parser.error("Please specify the files to trash.")

        reporter = TrashPutReporter(self.get_logger(options.verbose,argv[0]))

        self.trashcan = GlobalTrashCan(
                reporter = reporter,
                fstab = self.fstab,
                home_trashcan = HomeTrashCan(self.environ))
        self.trash_all(args)

        if reporter.all_files_have_been_trashed:
            return EX_OK
        else:
            return EX_IOERR

    def trash_all(self, args):
        for arg in args :
            self.trash(arg)

    def trash(self, arg):
        self.trashcan.trash(arg)

    def get_option_parser(self, program_name):
        from optparse import OptionParser

        parser = OptionParser(prog=program_name,
                              usage="%prog [OPTION]... FILE...",
                              description="Put files in trash",
                              version="%%prog %s" % version,
                              formatter=NoWrapFormatter(),
                              epilog=
"""To remove a file whose name starts with a `-', for example `-foo',
use one of these commands:

    trash -- -foo

    trash ./-foo

Report bugs to http://code.google.com/p/trash-cli/issues""")
        parser.add_option("-d",
                          "--directory",
                          action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-f",
                          "--force",
                          action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-i",
                          "--interactive",
                          action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-r",
                          "-R",
                          "--recursive",
                          action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-v",
                          "--verbose",
                          action="store_true",
                          help="explain what is being done",
                          dest="verbose")
        def patched_print_help():
            encoding = parser._get_encoding(self.stdout)
            self.stdout.write(parser.format_help().encode(encoding, "replace"))
        def patched_error(msg):
            parser.print_usage(self.stderr)
            parser.exit(2, "%s: error: %s\n" % (program_name, msg))
        def patched_exit(status=0, msg=None):
            if msg: self.stderr.write(msg)
            import sys
            sys.exit(status)

        parser.print_help = patched_print_help
        parser.error = patched_error
        parser.exit = patched_exit
        return parser

    def get_logger(self,verbose,argv0):
        import os.path
        class MyLogger:
            def __init__(self, stderr):
                self.program_name = os.path.basename(argv0)
                self.stderr=stderr
            def info(self,message):
                if verbose:
                    self.emit(message)
            def warning(self,message):
                self.emit(message)
            def emit(self, message):
                self.stderr.write("%s: %s\n" % (self.program_name,message))

        return MyLogger(self.stderr)

class TrashPutReporter:
    def __init__(self, logger = NullObject()):
        self.logger = logger
        self.all_files_have_been_trashed = True

    def unable_to_trash_dot_entries(self,file):
        self.logger.warning("cannot trash %s `%s'" % (describe(file), file))

    def unable_to_trash_file(self,f):
        self.logger.warning("cannot trash %s `%s'" % (describe(f), f))
        self.all_files_have_been_trashed = False

    def file_has_been_trashed_in_as(self, trashee, trash_directory, destination):
        self.logger.info("`%s' trashed in %s" % (trashee, trash_directory))

    def found_unsercure_trash_dir_symlink(self, trash_dir_path):
        self.logger.info("found unsecure .Trash dir (should not be a symlink): %s"
                % trash_dir_path)
    def found_unusable_trash_dir_not_a_dir(self, trash_dir_path):
        self.logger.info("found unusable .Trash dir (should be a dir): %s"
                % trash_dir_path)
    def found_unsecure_trash_dir_unsticky(self, trash_dir_path):
        self.logger.info("found unsecure .Trash dir (should be sticky): %s"
                % trash_dir_path)
    def unable_to_trash_file_in_because(self,
                                        file_to_be_trashed,
                                        trash_directory, error):
        self.logger.info("Failed to trash %s in %s, because :%s" %
                         (file_to_be_trashed, trash_directory, error))


def describe(path):
    """
    Return a textual description of the file pointed by this path.
    Options:
     - "symbolic link"
     - "directory"
     - "`.' directory"
     - "`..' directory"
     - "regular file"
     - "regular empty file"
     - "non existent"
     - "entry"
    """
    if os.path.islink(path):
        return 'symbolic link'
    elif os.path.isdir(path):
        if path == '.':
            return 'directory'
        elif path == '..':
            return 'directory'
        else:
            if os.path.basename(path) == '.':
                return "`.' directory"
            elif os.path.basename(path) == '..':
                return "`..' directory"
            else:
                return 'directory'
    elif os.path.isfile(path):
        if os.path.getsize(path) == 0:
            return 'regular empty file'
        else:
            return 'regular file'
    elif not os.path.exists(path):
        return 'non existent'
    else:
        return 'entry'

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
    def is_int(self, text):
        try:
            int(text)
            return True
        except ValueError:
            return False
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

    def valid_to_be_written(self, trash_dir_path, output):
        parent = os.path.dirname(trash_dir_path)
        if not self.fs.isdir(parent):
            output.not_valid_should_be_a_dir()
            return
        if self.fs.islink(parent):
            output.not_valid_parent_should_not_be_a_symlink()
            return
        if not self.fs.has_sticky_bit(parent):
            output.not_valid_parent_should_be_sticky()
            return
        output.is_valid()

class TopDirWithoutStickyBit(IOError): pass
class TopDirNotPresent(IOError): pass
class TopDirIsSymLink(IOError): pass

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
    def _trashinfos(self):
        for entry in self._trashinfo_entries():
            yield self._trashinfo(entry)
    def _trashinfo(self, entry):
        class TrashInfo:
            def __init__(self, info_dir, files_dir, entry, file_reader,
                         volume_path):
                self.info_dir    = info_dir
                self.files_dir   = files_dir
                self.entry       = entry
            def path_to_backup_copy(self):
                entry = self.entry[:-len('.trashinfo')]
                return os.path.join(self.files_dir, entry)
            def path_to_trashinfo(self):
                return os.path.join(self.info_dir, self.entry)
        return TrashInfo(self._info_dir(),
                         self._files_dir(),
                         entry,
                         self.file_reader,
                         self.volume_path)
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

def maybe_date(parsing_closure):

    try:
        date = parsing_closure()
    except ValueError:
        return unknown_date()
    else:
        if date: return date
    return unknown_date()

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

