import os
import sys

from .trash import HomeTrashCan
from .trash import EX_OK, EX_IOERR
from .trash import version
from .trash import TrashDirectories
from .fstab import Fstab
from .fs import has_sticky_bit
from .fs import parent_of

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
                home_trashcan = HomeTrashCan(self.environ))
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

class TopDirWithoutStickyBit(IOError): pass
class TopDirNotPresent(IOError): pass
class TopDirIsSymLink(IOError): pass

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
        self.trash_directories = TrashDirectories(home_trashcan,
                self.volume_of, getuid, fstab.mount_points())

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
                          trashed_file['trash_directory_name'],
                          trashed_file['where_file_was_stored'])
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

    def _possible_trash_directories_for(self, file):
        volume = self.volume_of_parent(file)
        trash_dirs = []
        self.trash_directories.home_trash_dir(trash_dirs.append)
        self.trash_directories.for_volume(volume, trash_dirs.append)
        return trash_dirs
    def volume_of_parent(self, file):
        return self.volume_of(parent_of(file))


