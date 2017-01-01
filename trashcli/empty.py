from .trash import TopTrashDirRules
from .trash import TrashDirs
from .trash import Harvester
from .trash import EX_OK
from .trash import Parser
from .trash import PrintHelp
from .trash import PrintVersion
from .trash import EX_USAGE
from .trash import ParseTrashInfo
from .trash import CleanableTrashcan
import os

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

        self.out          = out
        self.err          = err
        self.file_reader  = file_reader
        self.environ      = environ
        self.getuid       = getuid
        self.list_volumes = list_volumes
        self.version      = version
        self._now         = now
        self.file_remover = file_remover
        self._dustman     = DeleteAnything()

    def run(self, *argv):
        self.program_name = os.path.basename(argv[0])
        self.exit_code    = EX_OK

        parse = Parser()
        parse.on_help(PrintHelp(self.description, self.println))
        parse.on_version(PrintVersion(self.println, self.version))
        parse.on_argument(self.set_max_age_in_days)
        parse.as_default(self.empty_all_trashdirs)
        parse.on_invalid_option(self.report_invalid_option_usage)
        parse.add_option('trash-dir=', self.empty_trashdir)

        parse(argv)

        return self.exit_code

    def set_max_age_in_days(self, arg):
        max_age_in_days = int(arg)
        self._dustman = DeleteAccordingDate(self.file_reader.contents_of,
                                            self._now,
                                            max_age_in_days)

    def report_invalid_option_usage(self, program_name, option):
        self.println_err("{program_name}: invalid option -- '{option}'"
                .format(**locals()))
        self.exit_code |= EX_USAGE

    def println_err(self, msg):
        self.err.write("{}\n".format(msg))

    def description(self, program_name, printer):
        printer.usage('Usage: %s [days]' % program_name)
        printer.summary('Purge trashed files.')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()

    def empty_trashdir(self, specific_dir):
        self.delete_all_things_under_trash_dir(specific_dir, None)
    def empty_all_trashdirs(self):
        trashdirs = TrashDirs(self.environ,
                              self.getuid,
                              self.list_volumes,
                              TopTrashDirRules(self.file_reader))
        trashdirs.on_trash_dir_found = self.delete_all_things_under_trash_dir

        trashdirs.list_trashdirs()

    def delete_all_things_under_trash_dir(self, trash_dir_path, volume_path):
        harvester = Harvester(self.file_reader)
        harvester.on_trashinfo_found = self.delete_trashinfo_and_backup_copy
        harvester.on_orphan_found = self.delete_orphan
        harvester.analize_trash_directory(trash_dir_path, volume_path)

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
    def print_cannot_remove_error(self, exc, path):
        error_message = "cannot remove {path}".format(path=path)
        self.println_err("{program_name}: {msg}".format(
            program_name=self.program_name,
            msg=error_message))
    def println(self, line):
        self.out.write(line + '\n')

class FileRemoveWithErrorHandling:
    def __init__(self, file_remover, on_error):
        self.file_remover = file_remover
        self.on_error = on_error
    def remove_file(self, path):
        try:
            return self.file_remover.remove_file(path)
        except OSError as e:
            self.on_error(e, path)
    def remove_file_if_exists(self, path):
        try:
            return self.file_remover.remove_file_if_exists(path)
        except OSError as e:
            self.on_error(e, path)

class DeleteAccordingDate:
    def __init__(self, contents_of, now, max_age_in_days):
        self._contents_of            = contents_of
        self._now                    = now
        self.max_age_in_days         = max_age_in_days
    def delete_if_ok(self, trashinfo_path, trashcan):
        contents = self._contents_of(trashinfo_path)
        ParseTrashInfo(
            on_deletion_date=IfDate(
                OlderThan(self.max_age_in_days, self._now),
                lambda: trashcan.delete_trashinfo_and_backup_copy(trashinfo_path)
            ),
        )(contents)

class DeleteAnything:
    def delete_if_ok(self, trashinfo_path, trashcan):
        trashcan.delete_trashinfo_and_backup_copy(trashinfo_path)

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

