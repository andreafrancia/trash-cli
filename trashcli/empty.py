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
        self.environ = environ
        self.getuid  = getuid
        self.list_volumes = list_volumes
        self.version      = version
        self._now         = now
        self._dustman     = DeleteAlways()
        self.file_remover = file_remover

    def run(self, *argv):
        self.program_name  = os.path.basename(argv[0])
        self.exit_code     = EX_OK

        parse = Parser()
        parse.on_help(PrintHelp(self.description, self.println))
        parse.on_version(PrintVersion(self.println, self.version))
        parse.on_argument(self.set_max_age_in_days)
        parse.as_default(self.empty_all_trashdirs)
        parse.on_invalid_option(self.report_invalid_option_usage)

        parse(argv)

        return self.exit_code

    def set_max_age_in_days(self, arg):
        max_age_in_days = int(arg)
        self._dustman = DeleteAccordingDate(self.file_reader.contents_of,
                                                 self._now,
                                                 max_age_in_days)

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
    def empty_all_trashdirs(self):
        class FileRemoveB:
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

        def on_error(exc, path):
            error_message = "cannot remove {path}".format(path=path)
            self.err.write("{program_name}: {msg}\n".format(
                program_name=self.program_name,
                msg=error_message))
        trashcan = CleanableTrashcan(FileRemoveB(self.file_remover,
                                                 on_error=on_error))
        def delete_if_expired(trashinfo_path):
            self._dustman.delete_if_ok(trashinfo_path, trashcan)
        harvester = Harvester(self.file_reader)
        harvester.on_trashinfo_found = delete_if_expired
        harvester.on_orphan_found = trashcan.delete_orphan
        trashdirs = TrashDirs(self.environ,
                              self.getuid,
                              self.list_volumes,
                              TopTrashDirRules(self.file_reader))
        trashdirs.on_trash_dir_found = harvester.analize_trash_directory
        trashdirs.list_trashdirs()
    def println(self, line):
        self.out.write(line + '\n')

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
class DeleteAlways:
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

