import collections

from .list import TrashDirsSelector
from .trash import TopTrashDirRules, TrashDir, path_of_backup_copy, \
    print_version, println, Clock, parse_deletion_date, trash_dir_found, UserInfoProvider, AllUsersInfoProvider
from .trash import TrashDirsScanner
from .trash import EX_OK
from .trash import PrintHelp
from .trash import EX_USAGE
import os
import sys
from trashcli.list_mount_points import os_mount_points
from datetime import datetime
from trashcli.fs import FileSystemReader
from trashcli.fs import FileRemover
from trashcli import trash


def main(argv=sys.argv,
         stdout=sys.stdout,
         stderr=sys.stderr,
         environ=os.environ):
    return EmptyCmd(
        out=stdout,
        err=stderr,
        environ=environ,
        list_volumes=os_mount_points,
        now=datetime.now,
        file_reader=FileSystemReader(),
        getuid=os.getuid,
        file_remover=FileRemover(),
        version=trash.version,
    ).run(*argv)


class Errors:
    def __init__(self, program_name, err):
        self.program_name = program_name
        self.err = err

    def print_error(self, msg):
        self.err.write("%s: %s\n" % (self.program_name, msg))


def description(program_name, printer):
    printer.usage('Usage: %s [days]' % program_name)
    printer.summary('Purge trashed files.')
    printer.options(
       "  --version   show program's version number and exit",
       "  -h, --help  show this help message and exit")
    printer.bug_reporting()


class EmptyCmd:
    def __init__(self,
                 out,
                 err,
                 environ,
                 list_volumes,
                 now,
                 file_reader,
                 getuid,
                 file_remover,
                 version):

        self.out = out
        self.err = err
        self.file_reader = file_reader
        self.version = version
        self.clock = Clock(now, environ)
        file_remover_with_error = FileRemoveWithErrorHandling(file_remover,
                                                              self.print_cannot_remove_error)
        self.trashcan = CleanableTrashcan(file_remover_with_error)
        user_info_provider = UserInfoProvider(environ, getuid)
        user_dir_scanner = TrashDirsScanner(user_info_provider,
                                            list_volumes,
                                            TopTrashDirRules(file_reader))
        all_users_info_provider = AllUsersInfoProvider()
        all_users_scanner = TrashDirsScanner(all_users_info_provider,
                                             list_volumes,
                                             TopTrashDirRules(file_reader))
        self.selector = TrashDirsSelector(user_dir_scanner.scan_trash_dirs(),
                                          all_users_scanner.scan_trash_dirs())

    def run(self, *argv):
        program_name = os.path.basename(argv[0])
        self.errors = Errors(program_name, self.err)

        result, args = parse_argv(argv[1:])

        exit_code = EX_OK
        if result == 'print_version':
            print_version(self.out, program_name, self.version)
        elif result == 'print_help':
            PrintHelp(description, self.out).my_print_help(program_name)
        elif result == 'invalid_option':
            invalid_option, = args
            self.errors.print_error("invalid option -- '%s'" % invalid_option)
            exit_code |= EX_USAGE
        elif result == 'print_time':
            now_value = self.clock.get_now_value(self.errors)
            println(self.out, now_value.replace(microsecond=0).isoformat())
        elif result == 'default':
            if not args.max_age_in_days:
                delete_mode = DeleteAnything()
            else:
                delete_mode = DeleteAccordingDate(self.file_reader.contents_of,
                                                  self.clock,
                                                  args.max_age_in_days,
                                                  self.errors)
            trash_dirs = self.selector.select(args.all_users,
                                              args.user_specified_trash_dirs)
            for event, args in trash_dirs:
                if event == trash_dir_found:
                    trash_dir_path, volume = args
                    trash_dir = TrashDir(self.file_reader)
                    for trashinfo_path in trash_dir.list_trashinfo(trash_dir_path):
                        if delete_mode.ok_to_delete(trashinfo_path):
                            self.trashcan.delete_trashinfo_and_backup_copy(trashinfo_path)
                    for orphan in trash_dir.list_orphans(trash_dir_path):
                        self.trashcan.delete_orphan(orphan)

        return exit_code

    def print_cannot_remove_error(self, path):
        self.errors.print_error("cannot remove %s" % path)


class FileRemoveWithErrorHandling:
    def __init__(self, file_remover, on_error):
        self.file_remover = file_remover
        self.on_error = on_error

    def remove_file(self, path):
        try:
            return self.file_remover.remove_file(path)
        except OSError:
            self.on_error(path)

    def remove_file_if_exists(self, path):
        try:
            return self.file_remover.remove_file_if_exists(path)
        except OSError:
            self.on_error(path)


class DeleteAccordingDate:
    def __init__(self, contents_of, clock, max_age_in_days, errors):
        self.contents_of = contents_of
        self.clock = clock
        self.max_age_in_days = max_age_in_days
        self.errors = errors

    def ok_to_delete(self, trashinfo_path):
        contents = self.contents_of(trashinfo_path)
        now_value = self.clock.get_now_value(self.errors)
        deletion_date = parse_deletion_date(contents)
        if deletion_date is not None:
            if older_than(self.max_age_in_days, now_value, deletion_date):
                return True
        return False


class DeleteAnything:

    def ok_to_delete(self, _trashinfo_path):
        return True


def older_than(days_ago, now_value, deletion_date):
    from datetime import timedelta
    limit_date = now_value - timedelta(days=days_ago)
    return deletion_date < limit_date


class CleanableTrashcan:
    def __init__(self, file_remover):
        self._file_remover = file_remover

    def delete_orphan(self, path_to_backup_copy):
        self._file_remover.remove_file(path_to_backup_copy)

    def delete_trashinfo_and_backup_copy(self, trashinfo_path):
        backup_copy = path_of_backup_copy(trashinfo_path)
        self._file_remover.remove_file_if_exists(backup_copy)
        self._file_remover.remove_file(trashinfo_path)


Parsed = collections.namedtuple('Parsed', ['all_users',
                                           'user_specified_trash_dirs',
                                           'max_age_in_days'])


def parse_argv(args):
    from getopt import getopt, GetoptError

    try:
        options, arguments = getopt(args,
                                    'h',
                                    ['help', 'version', 'trash-dir=',
                                     'print-time', 'all-users'])
    except GetoptError as e:
        invalid_option = e.opt
        return 'invalid_option', (invalid_option,)
    else:
        trash_dirs = []
        max_days = None
        all_users = False
        for option, value in options:
            if option in ('--help', '-h'):
                return 'print_help', ()
            if option == '--version':
                return 'print_version', ()
            if option == '--print-time':
                return 'print_time', ()
            if option == '--trash-dir':
                trash_dirs.append(value)
            if option == '--all-users':
                all_users = True
        for arg in arguments:
            max_days = int(arg)
        return 'default', Parsed(all_users, trash_dirs, max_days)
