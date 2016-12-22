import os
import sys

from .fs import parent_of
from .fstab import Fstab
from .trash import EX_OK, EX_IOERR
from .trash import TrashDirectories
from .trash import backup_file_path_from
from .trash import logger
from .trash import version
from datetime import datetime

def main():
    return TrashPutCmd(
        sys.stdout,
        sys.stderr
    ).run(sys.argv)

class TrashPutCmd:
    def __init__(self,
                 stdout,
                 stderr,
                 environ = os.environ,
                 volume_of = Fstab().volume_of):
        self.stdout    = stdout
        self.stderr    = stderr
        self.environ   = environ
        self.volume_of = volume_of
        self.logger    = MyLogger(self.stderr)
        self.reporter  = TrashPutReporter(self.logger)

    def run(self, argv):
        program_name = os.path.basename(argv[0])
        self.logger.use_program_name(program_name)

        parser = self.get_option_parser(program_name)
        try:
            (options, args) = parser.parse_args(argv[1:])
            if options.verbose: self.logger.be_verbose()

            if len(args) <= 0:
                parser.error("Please specify the files to trash.")
        except SystemExit,e:
            return e.code

        self.trashcan = GlobalTrashCan(
                reporter = self.reporter,
                volume_of = self.volume_of,
                environ = self.environ,
                fs = RealFs(),
                getuid = os.getuid,
                now = datetime.now)
        self.trash_all(args)

        return self.reporter.exit_code()

    def trash_all(self, args):
        for arg in args :
            self.trashcan.trash(arg)

    def get_option_parser(self, program_name):
        from optparse import OptionParser

        parser = OptionParser(prog=program_name,
                              usage="%prog [OPTION]... FILE...",
                              description="Put files in trash",
                              version="%%prog %s" % version,
                              formatter=NoWrapFormatter(),
                              epilog=epilog)
        parser.add_option("-d", "--directory", action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-f", "--force", action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-i", "--interactive", action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-r", "-R", "--recursive", action="store_true",
                          help="ignored (for GNU rm compatibility)")
        parser.add_option("-v", "--verbose", action="store_true",
                          help="explain what is being done", dest="verbose")
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

epilog="""\
To remove a file whose name starts with a `-', for example `-foo',
use one of these commands:

    trash -- -foo

    trash ./-foo

Report bugs to https://github.com/andreafrancia/trash-cli/issues"""

class MyLogger:
    def __init__(self, stderr):
        self.program_name = 'ERROR'
        self.stderr=stderr
        self.verbose = False
    def use_program_name(self, program_name):
        self.program_name = program_name
    def be_verbose(self):
        self.verbose = True
    def info(self,message):
        if self.verbose:
            self.emit(message)
    def warning(self,message):
        self.emit(message)
    def emit(self, message):
        self.stderr.write("%s: %s\n" % (self.program_name,message))

from optparse import IndentedHelpFormatter
class NoWrapFormatter(IndentedHelpFormatter) :
    def _format_text(self, text) :
        "[Does not] format a text, return the text as it is."
        return text

class NullObject:
    def __getattr__(self, name):
        return lambda *argl,**args:None

class TrashPutReporter:
    def __init__(self, logger = NullObject()):
        self.logger = logger
        self.some_file_has_not_be_trashed = False
        self.no_argument_specified = False
    def unable_to_trash_dot_entries(self,file):
        self.logger.warning("cannot trash %s `%s'" % (describe(file), file))
    def unable_to_trash_file(self,f):
        self.logger.warning("cannot trash %s `%s'" % (describe(f), f))
        self.some_file_has_not_be_trashed = True
    def file_has_been_trashed_in_as(self, trashee, trash_directory, destination):
        self.logger.info("`%s' trashed in %s" % (trashee,
                                                 shrinkuser(trash_directory)))
    def found_unsercure_trash_dir_symlink(self, trash_dir_path):
        self.logger.info("found unsecure .Trash dir (should not be a symlink): %s"
                % trash_dir_path)
    def invalid_top_trash_is_not_a_dir(self, trash_dir_path):
        self.logger.info("found unusable .Trash dir (should be a dir): %s"
                % trash_dir_path)
    def found_unsecure_trash_dir_unsticky(self, trash_dir_path):
        self.logger.info("found unsecure .Trash dir (should be sticky): %s"
                % trash_dir_path)
    def unable_to_trash_file_in_because(self,
                                        file_to_be_trashed,
                                        trash_directory, error):
        self.logger.info("Failed to trash %s in %s, because :%s" % (
           file_to_be_trashed, shrinkuser(trash_directory), error))
    def exit_code(self):
        if not self.some_file_has_not_be_trashed:
            return EX_OK
        else:
            return EX_IOERR

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

class RealFs:
    def __init__(self):
        import os
        from . import fs
        self.move           = fs.move
        self.atomic_write   = fs.atomic_write
        self.remove_file    = fs.remove_file
        self.ensure_dir     = fs.ensure_dir
        self.isdir          = os.path.isdir
        self.islink         = os.path.islink
        self.has_sticky_bit = fs.has_sticky_bit

class GlobalTrashCan:
    class NullReporter:
        def __getattr__(self,name):
            return lambda *argl,**args:None
    def __init__(self, environ, volume_of, reporter, fs, getuid, now):
        self.getuid        = getuid
        self.reporter      = reporter
        self.volume_of     = volume_of
        self.now           = now
        self.fs            = fs
        self.trash_directories = TrashDirectories(
                self.volume_of, getuid, environ)

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

        candidates = PossibleTrashDirectories(self.fs)
        self._possible_trash_directories_for(file, candidates)
        file_has_been_trashed = False
        for trash_dir in candidates.trash_dirs:
            if self._is_trash_dir_secure(trash_dir):
                if self._file_could_be_trashed_in(file, trash_dir.path):
                    try:
                        trashed_file = trash_dir.trash(file)
                        self.reporter.file_has_been_trashed_in_as(
                            file,
                            trashed_file['trash_directory'],
                            trashed_file['where_file_was_stored'])
                        file_has_been_trashed = True

                    except (IOError, OSError), error:
                        self.reporter.unable_to_trash_file_in_because(
                                file, trash_dir.path, str(error))

            if file_has_been_trashed: break

        if not file_has_been_trashed:
            self.reporter.unable_to_trash_file(file)

    def _is_trash_dir_secure(self, trash_dir):
        class ValidationOutput:
            def __init__(self):
                self.valid = True
            def not_valid_should_be_a_dir(_):
                self.reporter.invalid_top_trash_is_not_a_dir(
                        os.path.dirname(trash_dir.path))
                self.valid = False
            def not_valid_parent_should_not_be_a_symlink(_):
                self.reporter.found_unsercure_trash_dir_symlink(
                        os.path.dirname(trash_dir.path))
                self.valid = False
            def not_valid_parent_should_be_sticky(_):
                self.reporter.found_unsecure_trash_dir_unsticky(
                        os.path.dirname(trash_dir.path))
                self.valid = False
            def is_valid(self):
                self.valid = True
        output = ValidationOutput()
        trash_dir.checker.fs = self.fs
        trash_dir.checker.valid_to_be_written(trash_dir.path, output)
        return output.valid

    def _should_skipped_by_specs(self, file):
        basename = os.path.basename(file)
        return (basename == ".") or (basename == "..")

    def _file_could_be_trashed_in(self,file_to_be_trashed,trash_dir_path):
        return self.volume_of(trash_dir_path) == self.volume_of_parent(file_to_be_trashed)

    def _possible_trash_directories_for(self, file, candidates):
        volume = self.volume_of_parent(file)

        self.trash_directories.home_trash_dir(
                candidates.add_home_trash)
        self.trash_directories.volume_trash_dir1(
                volume, candidates.add_top_trash_dir)
        self.trash_directories.volume_trash_dir2(
                volume, candidates.add_alt_top_trash_dir)
        return candidates

    def volume_of_parent(self, file):
        return self.volume_of(parent_of(file))

class PossibleTrashDirectories:
    def __init__(self, fs):
        self.trash_dirs = []
        self.fs = fs
    def add_home_trash(self, path, volume):
        trash_dir = self._make_trash_dir(path, volume)
        trash_dir.store_absolute_paths()
        self.trash_dirs.append(trash_dir)
    def add_top_trash_dir(self, path, volume):
        trash_dir = self._make_trash_dir(path, volume)
        trash_dir.store_relative_paths()
        trash_dir.checker = TopTrashDirWriteRules(None)
        self.trash_dirs.append(trash_dir)
    def add_alt_top_trash_dir(self, path, volume):
        trash_dir = self._make_trash_dir(path, volume)
        trash_dir.store_relative_paths()
        self.trash_dirs.append(trash_dir)
    def _make_trash_dir(self, path, volume):
        return TrashDirectoryForPut(path, volume, datetime.now, self.fs)

class TrashDirectoryForPut:
    from datetime import datetime
    def __init__(self, path, volume, now, fs):
        self.path      = os.path.normpath(path)
        self.volume    = volume
        self.logger    = logger
        self.info_dir  = os.path.join(self.path, 'info')
        self.files_dir = os.path.join(self.path, 'files')
        class all_is_ok_checker:
            def valid_to_be_written(self, a, b): pass
            def check(self, a):pass
        self.checker      = all_is_ok_checker()
        self.now          = now
        self.move         = fs.move
        self.atomic_write = fs.atomic_write
        self.remove_file  = fs.remove_file
        self.ensure_dir   = fs.ensure_dir

        self.path_for_trash_info = OriginalLocation(os.path.realpath)

    def store_absolute_paths(self):
        self.path_for_trash_info.make_absolutes_paths()

    def store_relative_paths(self):
        self.path_for_trash_info.make_paths_relatives_to(self.volume)

    def trash(self, path):
        path = os.path.normpath(path)

        original_location = self.path_for_trash_info.for_file(path)

        basename = os.path.basename(original_location)
        content = self.format_trashinfo(original_location, self.now())
        trash_info_file = self.persist_trash_info( self.info_dir, basename,
                content)

        where_to_store_trashed_file = backup_file_path_from(trash_info_file)

        self.ensure_files_dir_exists()

        try :
            self.move(path, where_to_store_trashed_file)
        except IOError as e :
            self.remove_file(trash_info_file)
            raise e
        result = dict()
        result['trash_directory'] = self.path
        result['where_file_was_stored'] = where_to_store_trashed_file
        return result

    def format_trashinfo(self, original_location, deletion_date):
        def format_date(deletion_date):
            return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")
        def format_original_location(original_location):
            import urllib
            return urllib.quote(original_location,'/')
        content = ("[Trash Info]\n" +
                   "Path=%s\n" % format_original_location(original_location) +
                   "DeletionDate=%s\n" % format_date(deletion_date))
        return content

    def ensure_files_dir_exists(self):
        self.ensure_dir(self.files_dir, 0700)

    def persist_trash_info(self, info_dir, basename, content) :
        """
        Create a .trashinfo file in the $trash/info directory.
        returns the created TrashInfoFile.
        """

        self.ensure_dir(info_dir, 0700)

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

            dest = os.path.join(info_dir, trash_info_basename)
            try :
                self.atomic_write(dest, content)
                self.logger.debug(".trashinfo created as %s." % dest)
                return dest
            except OSError:
                self.logger.debug("Attempt for creating %s failed." % dest)

            index += 1

        raise IOError()

def shrinkuser(path, environ=os.environ):
    import posixpath
    import re
    try:
        home_dir = environ['HOME']
        home_dir = posixpath.normpath(home_dir)
        if home_dir != '':
            path = re.sub('^' + re.escape(home_dir + os.path.sep),
                            '~' + os.path.sep, path)
    except KeyError:
        pass
    return path

class TopTrashDirWriteRules:
    def __init__(self, fs):
        self.fs = fs

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

class OriginalLocation:
    def __init__(self, realpath):
        self.realpath = realpath
        self.make_absolutes_paths()

    def make_paths_relatives_to(self, topdir):
        self.path_maker = TopDirRelativePaths(topdir)

    def make_absolutes_paths(self):
        self.path_maker = AbsolutePaths()

    def for_file(self, path):
        self.normalized_path = os.path.normpath(path)

        basename = os.path.basename(self.normalized_path)
        parent   = self._real_parent()

        parent = self.path_maker.calc_parent_path(parent)

        return os.path.join(parent, basename)

    def _real_parent(self):
        parent = os.path.dirname(self.normalized_path)
        return self.realpath(parent)

class TopDirRelativePaths:
    def __init__(self, topdir):
        self.topdir = topdir
    def calc_parent_path(self, parent):
        if (parent == self.topdir) or parent.startswith(self.topdir+os.path.sep) :
            parent = parent[len(self.topdir+os.path.sep):]
        return parent

class AbsolutePaths:
    def calc_parent_path(self, parent):
        return parent
