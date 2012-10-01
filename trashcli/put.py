import os
import sys

from .fs import has_sticky_bit
from .fs import parent_of
from .fstab import Fstab
from .trash import EX_OK, EX_IOERR
from .trash import PathForTrashInfo
from .trash import TopTrashDirRules
from .trash import TrashDirectories
from .trash import backup_file_path_from
from .trash import logger
from .trash import version

def main():
    return TrashPutCmd(
        sys.stdout,
        sys.stderr
    ).run(sys.argv)

class TrashPutCmd:
    def __init__(self, stdout, stderr, environ = os.environ, fstab = Fstab()):
        self.stdout   = stdout
        self.stderr   = stderr
        self.environ  = environ
        self.fstab    = fstab
        self.logger   = MyLogger(self.stderr)
        self.reporter = TrashPutReporter(self.logger)

    def run(self, argv):
        program_name = os.path.basename(argv[0])
        self.logger.use_program_name(program_name)

        parser = self.get_option_parser(program_name)
        (options, args) = parser.parse_args(argv[1:])
        if options.verbose: self.logger.be_verbose()

        if len(args) <= 0:
            parser.error("Please specify the files to trash.")

        self.trashcan = GlobalTrashCan(
                reporter = self.reporter,
                fstab = self.fstab,
                environ = self.environ)
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

Report bugs to http://code.google.com/p/trash-cli/issues"""

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

class GlobalTrashCan:
    class NullReporter:
        def __getattr__(self,name):
            return lambda *argl,**args:None
    from datetime import datetime
    def __init__(self, environ,
                       reporter = NullReporter(),
                       getuid   = os.getuid,
                       fstab    = Fstab(),
                       now      = datetime.now):
        self.getuid        = getuid
        self.reporter      = reporter
        self.fstab         = fstab
        self.now           = now
        self.trash_directories = TrashDirectories(self.volume_of, getuid,
                fstab.mount_points(), environ)

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

        trash_dirs = self._possible_trash_directories_for(file)
        file_has_been_trashed = False
        for trash_dir in trash_dirs:
            if self._is_trash_dir_secure(trash_dir):
                if self._file_could_be_trashed_in(file, trash_dir.path):
                    try:
                        trashed_file = trash_dir.trash(file)
                        self.reporter.file_has_been_trashed_in_as(
                            file,
                            trashed_file['trash_directory_name'],
                            trashed_file['where_file_was_stored'])
                        file_has_been_trashed = True

                    except (IOError, OSError), error:
                        self.reporter.unable_to_trash_file_in_because(
                                file, trash_dir.name(), str(error))
            if file_has_been_trashed: break

        if not file_has_been_trashed:
            self.reporter.unable_to_trash_file(file)
    def _is_trash_dir_secure(self, trash_dir):
        class FileSystem:
            def isdir(self, path):
                return os.path.isdir(path)
            def islink(self, path):
                return os.path.islink(path)
            def has_sticky_bit(self, path):
                return has_sticky_bit(path)
        class ValidationOutput:
            def __init__(self):
                self.valid = False
            def not_valid_should_be_a_dir(_):
                self.reporter.found_unusable_trash_dir_not_a_dir(
                        os.path.dirname(trash_dir.path))
            def not_valid_parent_should_not_be_a_symlink(_):
                self.reporter.found_unsercure_trash_dir_symlink(
                        os.path.dirname(trash_dir.path))
            def not_valid_parent_should_be_sticky(_):
                self.reporter.found_unsecure_trash_dir_unsticky(
                        os.path.dirname(trash_dir.path))
            def is_valid(self):
                self.valid = True
        output = ValidationOutput()
        trash_dir.checker.fs = FileSystem()
        trash_dir.checker.valid_to_be_written(trash_dir.path, output)
        return output.is_valid

    def _should_skipped_by_specs(self, file):
        basename = os.path.basename(file)
        return (basename == ".") or (basename == "..")

    def volume_of(self, path):
        return self.fstab.volume_of(path)

    def _file_could_be_trashed_in(self,file_to_be_trashed,trash_dir_path):
        return self.volume_of(trash_dir_path) == self.volume_of_parent(file_to_be_trashed)

    def _possible_trash_directories_for(self, file):
        volume = self.volume_of_parent(file)
        possibilities = PossibleTrashDirectories()
        self.trash_directories.home_trash_dir(possibilities.add_home_trash)
        self.trash_directories.volume_trash_dir1(volume,
                possibilities.add_top_trash_dir)
        self.trash_directories.volume_trash_dir2(volume,
                possibilities.add_alt_top_trash_dir)
        return possibilities.trash_dirs
    def volume_of_parent(self, file):
        return self.volume_of(parent_of(file))

class PossibleTrashDirectories:
    def __init__(self):
        self.trash_dirs = []
    def add_home_trash(self, path, volume):
        trash_dir = self._make_trash_dir(path, volume)
        trash_dir.store_absolute_paths()
        self.trash_dirs.append(trash_dir)
    def add_top_trash_dir(self, path, volume):
        trash_dir = self._make_trash_dir(path, volume)
        trash_dir.store_relative_paths()
        trash_dir.checker = TopTrashDirRules(None)
        self.trash_dirs.append(trash_dir)
    def add_alt_top_trash_dir(self, path, volume):
        trash_dir = self._make_trash_dir(path, volume)
        trash_dir.store_relative_paths()
        self.trash_dirs.append(trash_dir)
    def _make_trash_dir(self, path, volume):
        fs = RealFs()
        return TrashDirectoryForPut(path, volume, fs = fs)

class RealFs:
    def __init__(self):
        from . import fs
        self.move         = fs.move
        self.atomic_write = fs.atomic_write
        self.remove_file  = fs.remove_file
        self.ensure_dir   = fs.ensure_dir

class TrashDirectoryForPut:
    from datetime import datetime
    def __init__(self, path, volume, now = datetime.now, fs = RealFs()):
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
        result['trash_directory_name'] = self.name()
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

