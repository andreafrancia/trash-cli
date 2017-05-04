from .fs import FileSystemReader
from .trash import version
from .trash import TopTrashDirRules
from .trash import TrashDirs
from .trash import Harvester
from .trash import Parser
from .trash import PrintHelp
from .trash import PrintVersion
from .trash import parse_deletion_date
from .trash import ParseError
from .trash import parse_path
from .trash import unknown_date

class ListCmd:
    def __init__(self, out,
                       err,
                       environ,
                       list_volumes,
                       getuid,
                       file_reader = FileSystemReader(),
                       version     = version):

        self.output       = ListCmdOutput(out, err)
        self.err          = self.output.err
        self.environ      = environ
        self.list_volumes = list_volumes
        self.getuid       = getuid
        self.file_reader  = file_reader
        self.contents_of  = file_reader.contents_of
        self.version      = version

    def run(self, *argv):
        parse=Parser()
        parse.on_help(PrintHelp(self.description, self.output.println))
        parse.on_version(PrintVersion(self.output.println, self.version))
        parse.as_default(self.list_trash)
        parse(argv)
    def list_trash(self):
        harvester = Harvester(self.file_reader)
        harvester.on_volume = self.output.set_volume_path
        harvester.on_trashinfo_found = self._print_trashinfo

        trashdirs = TrashDirs(self.environ,
                              self.getuid,
                              self.list_volumes,
                              TopTrashDirRules(self.file_reader))
        trashdirs.on_trashdir_skipped_because_parent_not_sticky = self.output.top_trashdir_skipped_because_parent_not_sticky
        trashdirs.on_trashdir_skipped_because_parent_is_symlink = self.output.top_trashdir_skipped_because_parent_is_symlink
        trashdirs.on_trash_dir_found = harvester.analize_trash_directory

        trashdirs.list_trashdirs()
    def _print_trashinfo(self, path):
        try:
            contents = self.contents_of(path)
        except IOError as e :
            self.output.print_read_error(e)
        else:
            deletion_date = parse_deletion_date(contents) or unknown_date()
            try:
                path = parse_path(contents)
            except ParseError:
                self.output.print_parse_path_error(path)
            else:
                self.output.print_entry(deletion_date, path)
    def description(self, program_name, printer):
        printer.usage('Usage: %s [OPTIONS...]' % program_name)
        printer.summary('List trashed files')
        printer.options(
           "  --version   show program's version number and exit",
           "  -h, --help  show this help message and exit")
        printer.bug_reporting()

class ListCmdOutput:
    def __init__(self, out, err):
        self.out = out
        self.err = err
    def println(self, line):
        self.out.write(line+'\n')
    def error(self, line):
        self.err.write(line+'\n')
    def print_read_error(self, error):
        self.error(str(error))
    def print_parse_path_error(self, offending_file):
        self.error("Parse Error: %s: Unable to parse Path." % (offending_file))
    def top_trashdir_skipped_because_parent_not_sticky(self, trashdir):
        self.error("TrashDir skipped because parent not sticky: %s"
                % trashdir)
    def top_trashdir_skipped_because_parent_is_symlink(self, trashdir):
        self.error("TrashDir skipped because parent is symlink: %s"
                % trashdir)
    def set_volume_path(self, volume_path):
        self.volume_path = volume_path
    def print_entry(self, maybe_deletion_date, relative_location):
        import os
        original_location = os.path.join(self.volume_path, relative_location)
        self.println("%s %s" %(maybe_deletion_date, original_location))
