import argparse
import os

from .fs import FileSystemReader
from .fstab import volume_of
from .trash import version, TrashDir
from .trash import TopTrashDirRules
from .trash import TrashDirsScanner
from .trash import PrintVersion
from .trash import parse_deletion_date
from .trash import ParseError
from .trash import parse_path
from .trash import unknown_date

def main():
    import sys
    import os
    from trashcli.list_mount_points import os_mount_points
    ListCmd(
        out          = sys.stdout,
        err          = sys.stderr,
        environ      = os.environ,
        getuid       = os.getuid,
        list_volumes = os_mount_points,
    ).run(*sys.argv)

class ListCmd:
    def __init__(self, out,
                       err,
                       environ,
                       list_volumes,
                       getuid,
                       file_reader = FileSystemReader(),
                       version     = version):

        self.out          = out
        self.output       = ListCmdOutput(out, err)
        self.err          = self.output.err
        self.environ      = environ
        self.list_volumes = list_volumes
        self.getuid       = getuid
        self.file_reader  = file_reader
        self.contents_of  = file_reader.contents_of
        self.version      = version

    def run(self, *argv):
        parser = maker_parser(os.path.basename(argv[0]))
        parsed = parser.parse_args(argv[1:])
        if parsed.version:
            version_printer = PrintVersion(self.out, self.version)
            version_printer.print_version(argv[0])
        else:
            self.list_trash(parsed.trash_dirs)

    def list_trash(self, user_specified_trash_dirs):
        trashdirs_scanner = TrashDirsScanner(self.environ,
                                             self.getuid,
                                             self.list_volumes,
                                             TopTrashDirRules(self.file_reader))
        trash_dirs = decide_trash_dirs(user_specified_trash_dirs,
                                       trashdirs_scanner.scan_trash_dirs())
        for event, args in trash_dirs:
            if event == TrashDirsScanner.Found:
                path, volume = args
                trash_dir = TrashDir(self.file_reader)
                for trash_info in trash_dir.list_trashinfo(path):
                    self._print_trashinfo(volume, trash_info)
            elif event == TrashDirsScanner.SkippedBecauseParentNotSticky:
                path, = args
                self.output.top_trashdir_skipped_because_parent_not_sticky(path)
            elif event == TrashDirsScanner.SkippedBecauseParentIsSymlink:
                path, = args
                self.output.top_trashdir_skipped_because_parent_is_symlink(path)

    def _print_trashinfo(self, volume, path):
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
                self.output.print_entry(volume, deletion_date, path)


def description(program_name, printer):
    printer.usage('Usage: %s [OPTIONS...]' % program_name)
    printer.summary('List trashed files')
    printer.options(
       "  --version   show program's version number and exit",
       "  -h, --help  show this help message and exit")
    printer.bug_reporting()


def decide_trash_dirs(user_specified_dirs,
                      system_dirs):
    if not user_specified_dirs:
        for dir in  system_dirs:
            yield dir
    for dir in user_specified_dirs:
        yield (TrashDirsScanner.Found, (dir, volume_of(dir)))

def maker_parser(prog):
    parser = argparse.ArgumentParser(prog=prog,
                                     description='List trashed files',
                                     epilog='Report bugs to https://github.com/andreafrancia/trash-cli/issues')
    parser.add_argument('--version', action='store_true', default=False,
                        help="show program's version number and exit")
    parser.add_argument('--trash-dir', action='append', default=[],
                        dest='trash_dirs',
                        help='specify the trash directory to use')
    return parser


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

    def print_entry(self, volume, maybe_deletion_date, relative_location):
        original_location = os.path.join(volume, relative_location)
        self.println("%s %s" %(maybe_deletion_date, original_location))
