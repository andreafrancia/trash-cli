from .trash import TopTrashDirRules, TrashDir, path_of_backup_copy, print_version, println, Clock
from .trash import TrashDirsScanner
from .trash import EX_OK
from .trash import PrintHelp
from .trash import EX_USAGE
from .trash import ParseTrashInfo
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
        self.environ = environ
        self.getuid = getuid
        self.list_volumes = list_volumes
        self.version = version
        self.clock = Clock(now, environ)
        self.file_remover = file_remover

    def run(self, *argv):
        program_name = os.path.basename(argv[0])
        self.errors = Errors(program_name, self.err)

        result, args = parse_argv(argv[1:])

        exit_code = EX_OK
        if result == 'print_version':
            print_version(self.out, program_name, self.version)
        elif result == 'print_help':
            PrintHelp(self.description, self.out).my_print_help(program_name)
        elif result == 'invalid_option':
            invalid_option, = args
            self.errors.print_error("invalid option -- '%s'" % invalid_option)
            exit_code |= EX_USAGE
        elif result == 'print_time':
            now_value = self.clock.get_now_value(self.errors)
            println(self.out, now_value.replace(microsecond=0).isoformat())
        elif result == 'default':
            trash_dirs, arguments, = args
            self._dustman = DeleteAnything()
            if len(trash_dirs) > 0:
                for trash_dir in trash_dirs:
                    self.empty_trashdir(trash_dir)
            else:
                for argument in arguments:
                    max_age_in_days = int(argument)
                    self._dustman = DeleteAccordingDate(self.file_reader.contents_of,
                                                        self.clock,
                                                        max_age_in_days,
                                                        self.errors)
                self.empty_all_trashdirs()

        return exit_code

    def description(self, program_name, printer):
        printer.usage('Usage: %s [days]' % program_name)
        printer.summary('Purge trashed files.')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()

    def empty_trashdir(self, specific_dir):
        self.delete_all_things_under_trash_dir(specific_dir)

    def empty_all_trashdirs(self):
        scanner = TrashDirsScanner(self.environ,
                                   self.getuid,
                                   self.list_volumes,
                                   TopTrashDirRules(self.file_reader))

        for event, args in scanner.scan_trash_dirs():
            if event == TrashDirsScanner.Found:
                path, volume = args
                self.delete_all_things_under_trash_dir(path)

    def delete_all_things_under_trash_dir(self, trash_dir_path):
        trash_dir = TrashDir(self.file_reader)
        for trash_info in trash_dir.list_trashinfo(trash_dir_path):
            self.delete_trashinfo_and_backup_copy(trash_info)
        for orphan in trash_dir.list_orphans(trash_dir_path):
            self.delete_orphan(orphan)

    def delete_trashinfo_and_backup_copy(self, trashinfo_path):
        trashcan = self.make_trashcan()
        self._dustman.delete_if_ok(trashinfo_path, trashcan)

    def delete_orphan(self, path_to_backup_copy):
        trashcan = self.make_trashcan()
        trashcan.delete_orphan(path_to_backup_copy)

    def make_trashcan(self):
        file_remover_with_error = FileRemoveWithErrorHandling(self.file_remover,
                                                              self.print_cannot_remove_error)
        trashcan = CleanableTrashcan(file_remover_with_error)
        return trashcan

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
        self._contents_of = contents_of
        self.clock = clock
        self.max_age_in_days = max_age_in_days
        self.errors = errors

    def delete_if_ok(self, trashinfo_path, trashcan):
        contents = self._contents_of(trashinfo_path)
        now_value = self.clock.get_now_value(self.errors)
        ParseTrashInfo(
            on_deletion_date=IfDate(
                OlderThan(self.max_age_in_days, now_value),
                lambda: trashcan.delete_trashinfo_and_backup_copy(trashinfo_path)
            ),
        )(contents)


class DeleteAnything:

    def delete_if_ok(self, trashinfo_path, trashcan):
        trashcan.delete_trashinfo_and_backup_copy(trashinfo_path)


class IfDate:
    def __init__(self, date_criteria, then):
        self.date_criteria = date_criteria
        self.then = then

    def __call__(self, date2):
        if self.date_criteria(date2):
            self.then()


class OlderThan:
    def __init__(self, days_ago, now_value):
        from datetime import timedelta
        self.limit_date = now_value - timedelta(days=days_ago)

    def __call__(self, deletion_date):
        return deletion_date < self.limit_date


class CleanableTrashcan:
    def __init__(self, file_remover):
        self._file_remover = file_remover

    def delete_orphan(self, path_to_backup_copy):
        self._file_remover.remove_file(path_to_backup_copy)

    def delete_trashinfo_and_backup_copy(self, trashinfo_path):
        backup_copy = path_of_backup_copy(trashinfo_path)
        self._file_remover.remove_file_if_exists(backup_copy)
        self._file_remover.remove_file(trashinfo_path)


def parse_argv(args):
    from getopt import getopt, GetoptError

    try:
        options, arguments = getopt(args,
                                    'h',
                                    ['help', 'version', 'trash-dir=',
                                     'print-time'])
    except GetoptError as e:
        invalid_option = e.opt
        return 'invalid_option', (invalid_option,)
    else:
        trash_dirs = []
        for option, value in options:
            if option in ('--help', '-h'):
                return 'print_help', ()
            if option == '--version':
                return 'print_version', ()
            if option == '--print-time':
                return 'print_time', ()
            if option == '--trash-dir':
                trash_dirs.append(value)
        return 'default', (trash_dirs, arguments)
