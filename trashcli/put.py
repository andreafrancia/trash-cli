import os
import sys
from .trash import GlobalTrashCan, HomeTrashCan
from .trash import EX_OK, EX_IOERR
from .trash import version
from .fstab import Fstab

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
