import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter, SUPPRESS
from grp import getgrgid
from io import StringIO
from pwd import getpwuid
from typing import Dict

from trashcli.shell_completion import add_argument_to, TRASH_DIRS, TRASH_FILES
from trashcli.trash import version, EX_OK, EX_IOERR


class TrashPutCmd:
    def __init__(self, stdout, stderr, trasher):
        self.stdout = stdout
        self.stderr = stderr
        self.trasher = trasher

    def run(self, argv, environ, uid):
        program_name = os.path.basename(argv[0])
        parser = make_parser(program_name, self.stdout, self.stderr)
        try:
            options = parser.parse_args(argv[1:])
            if len(options.files) <= 0:
                parser.error("Please specify the files to trash.")
        except SystemExit as e:
            return e.code
        else:
            logger = MyLogger(self.stderr, program_name, options.verbose)
            reporter = TrashPutReporter(logger, environ)
            result = self.trash_all(options.files,
                                    options.trashdir,
                                    logger,
                                    options.mode,
                                    reporter,
                                    options.forced_volume,
                                    program_name,
                                    environ,
                                    uid)

            return reporter.exit_code(result)

    def trash_all(self,
                  args,
                  user_trash_dir,
                  logger,  # type: MyLogger
                  mode,
                  reporter,
                  forced_volume,
                  program_name,
                  environ,
                  uid):
        result = TrashResult(False)
        for arg in args:
            result = self.trasher.trash(arg,
                                        user_trash_dir,
                                        result,
                                        logger,
                                        mode,
                                        reporter,
                                        forced_volume,
                                        program_name,
                                        environ,
                                        uid)
        return result


mode_force = 'force'
mode_interactive = 'interactive'


def make_parser(program_name, stdout, stderr):
    parser = ArgumentParser(prog=program_name,
                            usage="%(prog)s [OPTION]... FILE...",
                            description="Put files in trash",
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog="""\
To remove a file whose name starts with a '-', for example '-foo',
use one of these commands:

    trash -- -foo

    trash ./-foo

Report bugs to https://github.com/andreafrancia/trash-cli/issues""")
    add_argument_to(parser)
    parser.add_argument("-d", "--directory",
                        action="store_true",
                        help="ignored (for GNU rm compatibility)")
    parser.add_argument("-f", "--force",
                        action="store_const",
                        dest="mode",
                        const=mode_force,
                        help="silently ignore nonexistent files")
    parser.add_argument("-i", "--interactive",
                        action="store_const",
                        dest="mode",
                        const=mode_interactive,
                        help="prompt before every removal")
    parser.add_argument("-r", "-R", "--recursive",
                        action="store_true",
                        help="ignored (for GNU rm compatibility)")
    parser.add_argument("--trash-dir",
                        type=str,
                        action="store", dest='trashdir',
                        help='use TRASHDIR as trash folder'
                        ).complete = TRASH_DIRS
    parser.add_argument("-v",
                        "--verbose",
                        default=0,
                        action="count",
                        dest="verbose",
                        help="explain what is being done")
    parser.add_argument('--force-volume',
                        default=None,
                        action="store",
                        dest="forced_volume",
                        help=SUPPRESS)
    parser.add_argument("--version",
                        action="version",
                        version=version)
    parser.add_argument('files',
                        nargs='*'
                        ).complete = TRASH_FILES
    return parser


def describe(path):
    """
    Return a textual description of the file pointed by this path.
    Options:
     - "symbolic link"
     - "directory"
     - "'.' directory"
     - "'..' directory"
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
                return "'.' directory"
            elif os.path.basename(path) == '..':
                return "'..' directory"
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


class MyLogger:
    def __init__(self,
                 stderr,  # type: StringIO
                 program_name,  # type: str
                 verbose,  # type: int
                 ):
        self.program_name = program_name
        self.stderr = stderr
        self.verbose = verbose

    def debug(self, message):
        if self.verbose > 1:
            self.stderr.write("%s: %s\n" % (self.program_name, message))

    def debug_func_result(self, messages_func):
        if self.verbose > 1:
            for line in messages_func():
                self.stderr.write("%s: %s\n" % (self.program_name, line))

    def info(self, message):
        if self.verbose > 0:
            self.stderr.write("%s: %s\n" % (self.program_name, message))

    def warning2(self, message):
        self.stderr.write("%s: %s\n" % (self.program_name, message))


class TrashResult:
    def __init__(self, some_file_has_not_be_trashed):
        self.some_file_has_not_be_trashed = some_file_has_not_be_trashed

    def mark_unable_to_trash_file(self):
        return TrashResult(True)

    def __eq__(self, other):
        return self.some_file_has_not_be_trashed == \
               other.some_file_has_not_be_trashed

    def __repr__(self):
        return 'TrashResult(%s)' % self.some_file_has_not_be_trashed


class TrashPutReporter:
    def __init__(self, logger,
                 environ):  # type: (MyLogger, Dict[str, str]) -> None
        self.logger = logger
        self.no_argument_specified = False
        self.environ = environ

    def unable_to_trash_dot_entries(self, file):
        self.logger.warning2("cannot trash %s '%s'" % (describe(file), file))

    def unable_to_trash_file(self, f):
        self.logger.warning2("cannot trash %s '%s'" % (describe(f), f))

    def file_has_been_trashed_in_as(self, trashee, trash_directory):
        self.logger.info("'%s' trashed in %s" % (trashee,
                                                 shrink_user(trash_directory,
                                                             self.environ)))

    def trash_dir_is_not_secure(self, path):
        self.logger.info("trash directory %s is not secure" % path)

    def log_info(self, message):
        self.logger.info(message)

    def unable_to_trash_file_in_because(self,
                                        file_to_be_trashed,
                                        trash_directory, error):
        self.logger.info("Failed to trash %s in %s, because: %s" % (
            file_to_be_trashed, shrink_user(trash_directory,
                                            self.environ), error))
        self.logger.debug_func_result(
            lambda: self.log_data_for_debugging(error))

    @classmethod
    def log_data_for_debugging(cls, error):
        try:
            filename = error.filename
        except AttributeError:
            pass
        else:
            for path in [filename, os.path.dirname(filename)]:
                info = cls.get_stats(path)
                yield "stats for %s: %s" % (path, info)

    @staticmethod
    def get_stats(path):
        try:
            stats = os.stat(path, follow_symlinks=False)
            user = getpwuid(stats.st_uid).pw_name
            group = getgrgid(stats.st_gid).gr_name
            perms = oct(stats.st_mode & 0o777).replace('0o', '')
            return "%s %s %s" % (perms, user, group)
        except OSError as e:
            return str(e)

    def trash_dir_with_volume(self, trash_dir_path, volume_path):
        self.logger.info("Trash-dir: %s from volume: %s" % (trash_dir_path,
                                                            volume_path))

    def exit_code(self, result):
        if not result.some_file_has_not_be_trashed:
            return EX_OK
        else:
            return EX_IOERR

    def volume_of_file(self, volume):
        self.logger.info("Volume of file: %s" % volume)


def shrink_user(path, environ):
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
