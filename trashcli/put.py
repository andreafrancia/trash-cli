import errno
import os
import sys
import random
from datetime import datetime

from .fstab import volumes
from .trash import EX_OK, EX_IOERR, home_trash_dir, volume_trash_dir1, \
    volume_trash_dir2, my_input
from .trash import path_of_backup_copy
from .trash import version


def main():
    trash_directories_finder = TrashDirectoriesFinder(os.environ,
                                                      os.getuid,
                                                      volumes)
    file_trasher = FileTrasher(RealFs(),
                               volumes,
                               os.path.realpath,
                               datetime.now,
                               trash_directories_finder,
                               parent_path)
    access = Access()
    user = User(my_input)
    trasher = Trasher(file_trasher, user, access)
    cmd = TrashPutCmd(sys.stdout, sys.stderr, os.environ, trasher)
    return cmd.run(sys.argv)


def parent_path(path):
    return os.path.realpath(os.path.dirname(path))


class Access:
    @staticmethod
    def is_accessible(file):
        return os.access(file, os.F_OK)


class TrashPutCmd:
    def __init__(self, stdout, stderr, environ, trasher):
        self.stdout = stdout
        self.stderr = stderr
        self.environ = environ
        self.trasher = trasher

    def run(self, argv):
        program_name  = os.path.basename(argv[0])
        parser = get_option_parser(program_name, self.stdout, self.stderr)
        try:
            (options, args) = parser.parse_args(argv[1:])

            if len(args) <= 0:
                parser.error("Please specify the files to trash.")
        except SystemExit as e:
            return e.code
        else:
            logger = MyLogger(self.stderr, program_name, options.verbose)
            reporter = TrashPutReporter(logger, self.environ)
            result = self.trash_all(args,
                                    options.trashdir,
                                    logger,
                                    options.mode,
                                    reporter,
                                    options.forced_volume,
                                    program_name)

            return reporter.exit_code(result)

    def trash_all(self,
                  args,
                  user_trash_dir,
                  logger,
                  mode,
                  reporter,
                  forced_volume,
                  program_name):
        result = TrashResult(False)
        for arg in args :
            result = self.trasher.trash(arg,
                                        user_trash_dir,
                                        result,
                                        logger,
                                        mode,
                                        reporter,
                                        forced_volume,
                                        program_name)
        return result


mode_force = 'force'
mode_interactive = 'interactive'


class User:
    def __init__(self, my_input):
        self.my_input = my_input

    def ask_user_about_deleting_file(self, program_name, path):
        reply = self.my_input("%s: trash %s '%s'? " % (program_name,
                                                        describe(path),
                                                        path))
        return parse_user_reply(reply)


user_replied_no = "user_replied_no"
user_replied_yes = "user_replied_yes"


def parse_user_reply(reply):
    return {False: user_replied_no,
            True: user_replied_yes}[reply.lower().startswith("y")]


class Trasher:
    def __init__(self, file_trasher, user, access):
        self.file_trasher = file_trasher
        self.user = user
        self.access = access

    def trash(self,
              file,
              user_trash_dir,
              result,
              logger,
              mode,
              reporter,
              forced_volume,
              program_name) :
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
            reporter.unable_to_trash_dot_entries(file)
            return result

        if mode == mode_force and not self.access.is_accessible(file):
            return result

        if mode == mode_interactive and self.access.is_accessible(file):
            reply = self.user.ask_user_about_deleting_file(program_name, file)
            if reply == user_replied_no:
                return result

        return self.file_trasher.trash_file(file,
                                            forced_volume,
                                            user_trash_dir,
                                            result,
                                            logger,
                                            reporter)

    def _should_skipped_by_specs(self, file):
        basename = os.path.basename(file)
        return (basename == ".") or (basename == "..")


class FileTrasher:

    def __init__(self, fs, volumes, realpath, now, trash_directories_finder,
                 parent_path):
        self.fs = fs
        self.volumes = volumes
        self.realpath = realpath
        self.now = now
        self.trash_directories_finder = trash_directories_finder
        self.parent_path = parent_path

    def trash_file(self,
                   file,
                   forced_volume,
                   user_trash_dir,
                   result,
                   logger,
                   reporter):
        volume_of_file_to_be_trashed = forced_volume or \
                                       self.volume_of_parent(file)
        candidates = self.trash_directories_finder.\
            possible_trash_directories_for(volume_of_file_to_be_trashed,
                                           user_trash_dir)
        reporter.volume_of_file(volume_of_file_to_be_trashed)
        file_has_been_trashed = False
        for path, volume, path_maker, checker in candidates:
            suffix = Suffix(random.randint)
            info_dir_path = os.path.join(path, 'info')
            info_dir = InfoDir(info_dir_path, self.fs, logger, suffix)
            path_maker = {absolute_paths: AbsolutePaths(),
                          relative_paths: TopDirRelativePaths(volume)}[path_maker]
            checker = {top_trash_dir_rules:TopTrashDirRules(),
                       all_is_ok_rules:AllIsOkRules()}[checker]
            trash_dir = TrashDirectoryForPut(path,
                                             volume,
                                             self.fs,
                                             path_maker,
                                             info_dir)
            trash_dir_is_secure, messages = checker.check_trash_dir_is_secure(
                trash_dir.path,
                self.fs)
            for message in messages:
                reporter.log_info(message)

            if trash_dir_is_secure:
                volume_of_trash_dir = self.volumes.volume_of(self.realpath(trash_dir.path))
                reporter.trash_dir_with_volume(trash_dir.path,
                                               volume_of_trash_dir)
                if self._file_could_be_trashed_in(volume_of_file_to_be_trashed,
                                                  volume_of_trash_dir):
                    try:
                        self.fs.ensure_dir(os.path.join(path, 'files'), 0o700)
                        trash_dir.trash2(file, self.now)
                        reporter.file_has_been_trashed_in_as(
                            file,
                            trash_dir.path)
                        file_has_been_trashed = True

                    except (IOError, OSError) as error:
                        reporter.unable_to_trash_file_in_because(
                            file, trash_dir.path, str(error))

            if file_has_been_trashed: break

        if not file_has_been_trashed:
            result = result.mark_unable_to_trash_file()
            reporter.unable_to_trash_file(file)

        return result


    def _file_could_be_trashed_in(self,
                                  volume_of_file_to_be_trashed,
                                  volume_of_trash_dir):
        return volume_of_trash_dir == volume_of_file_to_be_trashed

    def volume_of_parent(self, file):
        return self.volumes.volume_of(self.parent_path(file))


def get_option_parser(program_name, stdout, stderr):
    from optparse import OptionParser

    parser = OptionParser(prog=program_name,
                          usage="%prog [OPTION]... FILE...",
                          description="Put files in trash",
                          version="%%prog %s" % version,
                          formatter=NoWrapFormatter(),
                          epilog="""\
To remove a file whose name starts with a '-', for example '-foo',
use one of these commands:

    trash -- -foo

    trash ./-foo

Report bugs to https://github.com/andreafrancia/trash-cli/issues""")

    parser.add_option("-d", "--directory",
                      action="store_true",
                      help="ignored (for GNU rm compatibility)")
    parser.add_option("-f", "--force",
                      action="store_const",
                      dest="mode",
                      const=mode_force,
                      help="silently ignore nonexistent files")
    parser.add_option("-i", "--interactive",
                      action="store_const",
                      dest="mode",
                      const=mode_interactive,
                      help="prompt before every removal")
    parser.add_option("-r", "-R", "--recursive",
                      action="store_true",
                      help="ignored (for GNU rm compatibility)")
    parser.add_option("--trash-dir",
                      type='string',
                      action="store", dest='trashdir',
                      help='use TRASHDIR as trash folder')
    parser.add_option("-v",
                      "--verbose",
                      default=0,
                      action="count",
                      dest="verbose",
                      help="explain what is being done")
    parser.add_option('--force-volume',
                      default=None,
                      action="store",
                      dest="forced_volume",
                      help=SUPPRESS_HELP)
    original_print_help = parser.print_help
    def patched_print_help():
        original_print_help(stdout)
    def patched_error(msg):
        parser.print_usage(stderr)
        parser.exit(2, "%s: error: %s\n" % (program_name, msg))
    def patched_exit(status=0, msg=None):
        if msg: stderr.write(msg)
        import sys
        sys.exit(status)

    parser.print_help = patched_print_help
    parser.error = patched_error
    parser.exit = patched_exit
    return parser


absolute_paths = 'absolute_paths'
relative_paths = 'relative_paths'


class TrashDirectoriesFinder:
    def __init__(self, environ, getuid, volumes):
        self.environ = environ
        self.getuid = getuid
        self.volumes = volumes

    def possible_trash_directories_for(self,
                                       volume,
                                       specific_trash_dir):
        trash_dirs = []
        def add_home_trash(path, volume):
            trash_dirs.append((path, volume, absolute_paths, all_is_ok_rules))
        def add_top_trash_dir(path, volume):
            trash_dirs.append((path, volume, relative_paths, top_trash_dir_rules))
        def add_alt_top_trash_dir(path, volume):
            trash_dirs.append((path, volume, relative_paths, all_is_ok_rules))

        if specific_trash_dir:
            path = specific_trash_dir
            volume = self.volumes.volume_of(path)
            trash_dirs.append((path, volume, relative_paths, all_is_ok_rules))
        else:
            for path, dir_volume in home_trash_dir(self.environ,
                                                   self.volumes.volume_of):
                add_home_trash(path, dir_volume)
            for path, dir_volume in volume_trash_dir1(volume, self.getuid):
                add_top_trash_dir(path, dir_volume)
            for path, dir_volume in volume_trash_dir2(volume, self.getuid):
                add_alt_top_trash_dir(path, dir_volume)
        return trash_dirs


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
    def __init__(self, stderr, program_name, verbose):
        self.program_name = program_name
        self.stderr=stderr
        self.verbose = verbose

    def debug(self, message):
        if self.verbose > 1:
            self.stderr.write("%s: %s\n" % (self.program_name, message))

    def info(self,message):
        if self.verbose > 0:
            self.stderr.write("%s: %s\n" % (self.program_name, message))

    def warning2(self,message):
        self.stderr.write("%s: %s\n" % (self.program_name, message))


from optparse import IndentedHelpFormatter, SUPPRESS_HELP


class NoWrapFormatter(IndentedHelpFormatter) :
    def _format_text(self, text) :
        "[Does not] format a text, return the text as it is."
        return text


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
    def __init__(self, logger, environ):
        self.logger = logger
        self.no_argument_specified = False
        self.environ = environ
    def unable_to_trash_dot_entries(self,file):
        self.logger.warning2("cannot trash %s '%s'" % (describe(file), file))
    def unable_to_trash_file(self,f):
        self.logger.warning2("cannot trash %s '%s'" % (describe(f), f))
    def file_has_been_trashed_in_as(self, trashee, trash_directory):
        self.logger.info("'%s' trashed in %s" % (trashee,
                                                 shrink_user(trash_directory,
                                                             self.environ)))

    def log_info(self, message):
        self.logger.info(message)
    def unable_to_trash_file_in_because(self,
                                        file_to_be_trashed,
                                        trash_directory, error):
        self.logger.info("Failed to trash %s in %s, because: %s" % (
            file_to_be_trashed, shrink_user(trash_directory,
                                            self.environ), error))
    def trash_dir_with_volume(self, trash_dir_path, volume_path):
        self.logger.info("Trash-dir: %s from volume: %s" % (trash_dir_path,
                                                            volume_path))

    def exit_code(self, result):
        if not result.some_file_has_not_be_trashed:
            return EX_OK
        else:
            return EX_IOERR

    def volume_of_file(self,volume):
        self.logger.info("Volume of file: %s" % volume)

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

    def trash2(self, path, now):
        path = os.path.normpath(path)

        original_location = self.path_for_trash_info_for_file(path)

        basename = os.path.basename(original_location)
        content = format_trashinfo(original_location, now())
        trash_info_file = self.info_dir.persist_trash_info(basename, content)

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


class InfoDir:
    def __init__(self, path, fs, logger, suffix):
        self.path = path
        self.fs = fs
        self.logger = logger
        self.suffix = suffix

    def persist_trash_info(self, basename, content):
        """
        Create a .trashinfo file in the $trash/info directory.
        returns the created TrashInfoFile.
        """

        self.fs.ensure_dir(self.path, 0o700)

        index = 0
        name_too_long = False
        while True:
            suffix = self.suffix.suffix_for_index(index)
            trashinfo_basename = create_trashinfo_basename(basename,
                                                           suffix,
                                                           name_too_long)
            trashinfo_path = os.path.join(self.path, trashinfo_basename)
            try:
                self.fs.atomic_write(trashinfo_path, content)
                self.logger.debug(".trashinfo created as %s." % trashinfo_path)
                return trashinfo_path
            except OSError as e:
                if e.errno == errno.ENAMETOOLONG:
                    name_too_long = True
                self.logger.debug("Attempt for creating %s failed." % trashinfo_path)

            index += 1


def create_trashinfo_basename(basename, suffix, name_too_long):
    after_basename = suffix + ".trashinfo"
    if name_too_long:
        truncated_basename = basename[0:len(basename) - len(after_basename)]
    else:
        truncated_basename = basename
    return truncated_basename + after_basename


class Suffix:
    def __init__(self, randint):
        self.randint = randint

    def suffix_for_index(self, index):
        if index == 0:
            return ""
        elif index < 100:
            return "_%s" % index
        else:
            return "_%s" % self.randint(0, 65535)


def format_trashinfo(original_location, deletion_date):
    content = ("[Trash Info]\n" +
               "Path=%s\n" % format_original_location(original_location) +
               "DeletionDate=%s\n" % format_date(deletion_date)).encode('utf-8')
    return content


def format_date(deletion_date):
    return deletion_date.strftime("%Y-%m-%dT%H:%M:%S")


def format_original_location(original_location):
    try:
        from urllib import quote
    except ImportError:
        from urllib.parse import quote
    return quote(original_location,'/')


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


class AllIsOkRules:
    def check_trash_dir_is_secure(self, trash_dir_path, fs):
        return True, []


class TopTrashDirRules:
    def check_trash_dir_is_secure(self, trash_dir_path, fs):
        parent = os.path.dirname(trash_dir_path)
        if not fs.isdir(parent):
            return False, ["found unusable .Trash dir (should be a dir): %s" % parent]
        if fs.islink(parent):
            return False, ["found unsecure .Trash dir (should not be a symlink): %s" % parent]
        if not fs.has_sticky_bit(parent):
            return False, ["found unsecure .Trash dir (should be sticky): %s" % parent]
        return True, []


top_trash_dir_rules = 'top_trash_dir_rules'
all_is_ok_rules = 'all_is_ok_rules'

class OriginalLocation:
    def __init__(self, parent_realpath, path_maker):
        self.parent_realpath = parent_realpath
        self.path_maker = path_maker

    def for_file(self, path):
        self.normalized_path = os.path.normpath(path)

        basename = os.path.basename(self.normalized_path)
        parent   = self.parent_realpath(self.normalized_path)

        parent = self.path_maker.calc_parent_path(parent)

        return os.path.join(parent, basename)


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

