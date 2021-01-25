import sys
import os

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

def main():
    from trashcli.list_mount_points import os_mount_points
    ListCmd(
        out          = sys.stdout,
        err          = sys.stderr,
        environ      = os.environ,
        getuid       = os.getuid,
        list_volumes = os_mount_points,
    ).run(sys.argv)

def parse_args(sys_argv, curdir):
    import argparse
    parser = argparse.ArgumentParser(
        description='List trashed files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--sort',
                        choices=['date', 'path', 'none'],
                        default='date',
                        help='Sort list of list candidates by given field')
    parser.add_argument('--trash-dir',
                        action='store',
                        dest='trash_dir',
                        help=argparse.SUPPRESS)
    parser.add_argument('--version', action='store_true', default=False)
    parsed = parser.parse_args(sys_argv[1:])

    if parsed.version:
        return Command.PrintVersion, None
    else:
        return Command.RunList, {'sort': parsed.sort,
                                 'trash_dir': parsed.trash_dir}

class Command:
    PrintVersion = "Command.PrintVersion"
    RunList = "Command.RunList"

class TrashInfo:
    def __init__(self, deletion_date, original_location):
        self.deletion_date     = deletion_date
        self.original_location = original_location

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

    def run(self, argv):
        cmd, args = parse_args(argv, os.path.realpath(os.curdir) + os.path.sep)
        if cmd == Command.PrintVersion:
            command = os.path.basename(argv[0])
            self.output.println('%s %s' % (command, self.version))
            return
        elif cmd == Command.RunList:
            trash_dir_from_cli = args['trash_dir']
            trashed_files = self.list_trash()
            if args['sort'] == 'path':
                trashed_files = sorted(trashed_files, key=lambda x: x.original_location + str(x.deletion_date))
            elif args['sort'] == 'date':
                trashed_files = sorted(trashed_files, key=lambda x: x.deletion_date)
            for f in trashed_files:
                self.output.print_entry(f.deletion_date, f.original_location)

    def list_trash(self):
        self.deleted_files = []
        harvester = Harvester(self.file_reader)
        harvester.on_volume = self.output.set_volume_path
        harvester.on_trashinfo_found = self._append_trashinfo

        trashdirs = TrashDirs(self.environ,
                              self.getuid,
                              self.list_volumes,
                              TopTrashDirRules(self.file_reader))
        trashdirs.on_trashdir_skipped_because_parent_not_sticky = self.output.top_trashdir_skipped_because_parent_not_sticky
        trashdirs.on_trashdir_skipped_because_parent_is_symlink = self.output.top_trashdir_skipped_because_parent_is_symlink
        trashdirs.on_trash_dir_found = harvester.analize_trash_directory

        trashdirs.list_trashdirs()
        return self.deleted_files
    def _append_trashinfo(self, path):
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
                self.deleted_files.append(TrashInfo(deletion_date, path))

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
