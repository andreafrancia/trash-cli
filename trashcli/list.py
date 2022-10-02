# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import argparse
import os
import sys
from pprint import pprint

from trashcli.list_mount_points import os_mount_points
from trashcli.shell_completion import TRASH_DIRS, add_argument_to
from trashcli.super_enum import SuperEnum

from . import fstab
from .fs import FileSystemReader, file_size
from .fstab import Volumes, VolumesListing
from .trash import (
    AllUsersInfoProvider,
    DirChecker,
    ParseError,
    TrashDirReader,
    UserInfoProvider,
    maybe_parse_deletion_date,
    parse_path,
    path_of_backup_copy,
    print_version,
    version,
)
from .trash_dirs_scanner import (
    TopTrashDirRules,
    TrashDir,
    TrashDirsScanner,
    trash_dir_found,
    trash_dir_skipped_because_parent_is_symlink,
    trash_dir_skipped_because_parent_not_sticky,
)


def main():
    ListCmd(
        out=sys.stdout,
        err=sys.stderr,
        environ=os.environ,
        uid=os.getuid(),
        volumes_listing=VolumesListing(os_mount_points),
        volumes=fstab.volumes
    ).run(sys.argv)


class ListCmd:
    def __init__(self,
                 out,
                 err,
                 environ,
                 volumes_listing,
                 uid,
                 volumes,  # type: Volumes
                 file_reader=FileSystemReader(),
                 version=version,
                 ):

        self.out = out
        self.output = ListCmdOutput(out, err)
        self.err = self.output.err
        self.version = version
        self.file_reader = file_reader
        self.environ = environ
        self.uid = uid
        self.volumes_listing = volumes_listing
        self.selector = TrashDirsSelector.make(volumes_listing,
                                               file_reader,
                                               volumes)

    def run(self, argv):
        parser = Parser(os.path.basename(argv[0]))
        parsed = parser.parse_list_args(argv[1:])
        if parsed.action == Action.print_version:
            print_version(self.out, argv[0], self.version)
        elif parsed.action == Action.list_volumes:
            self.print_volumes_list()
        elif parsed.action == Action.debug_volumes:
            self.debug_volumes()
        elif parsed.action == Action.list_trash_dirs:
            self.list_trash_dirs(parsed.trash_dirs,
                                 parsed.all_users,
                                 self.environ,
                                 self.uid)
        elif parsed.action == Action.list_trash:
            extractor = {
                'deletion_date': DeletionDateExtractor(),
                'size': SizeExtractor(),
            }[parsed.attribute_to_print]
            self.list_trash(parsed.trash_dirs,
                            extractor,
                            parsed.show_files,
                            parsed.all_users,
                            self.environ,
                            self.uid)
        elif parsed.action == Action.print_python_executable:
            self.print_python_executable()
        else:
            raise ValueError('Unknown action: ' + parsed.action)

    def debug_volumes(self):
        import psutil
        import os
        all = sorted([p for p in psutil.disk_partitions(all=True)],
                     key=lambda p: p.device)
        physical = sorted([p for p in psutil.disk_partitions()],
                          key=lambda p: p.device)
        virtual = [p for p in all if p not in physical]
        print("physical ->")
        pprint(physical)
        print("virtual ->")
        pprint(virtual)
        os.system('df -P')

    def list_trash(self,
                   user_specified_trash_dirs,
                   extractor,
                   show_files,
                   all_users,
                   environ,
                   uid):
        trash_dirs = self.selector.select(all_users,
                                          user_specified_trash_dirs,
                                          environ,
                                          uid)
        for event, args in trash_dirs:
            if event == trash_dir_found:
                path, volume = args
                trash_dir = TrashDirReader(self.file_reader)
                for trash_info in trash_dir.list_trashinfo(path):
                    self._print_trashinfo(volume, trash_info, extractor,
                                          show_files)
            elif event == trash_dir_skipped_because_parent_not_sticky:
                path, = args
                self.output.top_trashdir_skipped_because_parent_not_sticky(path)
            elif event == trash_dir_skipped_because_parent_is_symlink:
                path, = args
                self.output.top_trashdir_skipped_because_parent_is_symlink(path)

    def list_trash_dirs(self,
                        user_specified_trash_dirs,
                        all_users,
                        environ,
                        uid):
        trash_dirs = self.selector.select(all_users,
                                          user_specified_trash_dirs,
                                          environ,
                                          uid)
        for event, args in trash_dirs:
            if event == trash_dir_found:
                path, volume = args
                print("%s" % path)
            elif event == trash_dir_skipped_because_parent_not_sticky:
                path = args
                print("parent_not_sticky: %s" % (path))
            elif event == trash_dir_skipped_because_parent_is_symlink:
                path = args
                print("parent_is_symlink: %s" % (path))

    def print_python_executable(self):
        import sys
        print(sys.executable)

    def _print_trashinfo(self, volume, trashinfo_path, extractor, show_files):
        try:
            contents = self.file_reader.contents_of(trashinfo_path)
        except IOError as e:
            self.output.print_read_error(e)
        else:
            try:
                relative_location = parse_path(contents)
            except ParseError:
                self.output.print_parse_path_error(trashinfo_path)
            else:
                attribute = extractor.extract_attribute(trashinfo_path,
                                                        contents)
                original_location = os.path.join(volume, relative_location)

                if show_files:
                    original_file = path_of_backup_copy(trashinfo_path)
                    line = format_line2(attribute, original_location,
                                        original_file)
                else:
                    line = format_line(attribute, original_location)
                self.output.println(line)

    def print_volumes_list(self):
        for volume in self.volumes_listing.list_volumes(self.environ):
            print(volume)


def format_line(attribute, original_location):
    return "%s %s" % (attribute, original_location)


def format_line2(attribute, original_location, original_file):
    return "%s %s -> %s" % (attribute, original_location, original_file)


class DeletionDateExtractor:
    def extract_attribute(self, _trashinfo_path, contents):
        return maybe_parse_deletion_date(contents)


class SizeExtractor:
    def extract_attribute(self, trashinfo_path, _contents):
        backup_copy = path_of_backup_copy(trashinfo_path)
        try:
            return str(file_size(backup_copy))
        except FileNotFoundError:
            if os.path.islink(backup_copy):
                return 0
            else:
                raise


def description(program_name, printer):
    printer.usage('Usage: %s [OPTIONS...]' % program_name)
    printer.summary('List trashed files')
    printer.options(
        "  --version   show program's version number and exit",
        "  -h, --help  show this help message and exit")
    printer.bug_reporting()


class TrashDirsSelector:
    def __init__(self,
                 current_user_dirs,
                 all_users_dirs,
                 volumes  # type: Volumes
                 ):
        self.current_user_dirs = current_user_dirs
        self.all_users_dirs = all_users_dirs
        self.volumes = volumes

    def select(self,
               all_users_flag,
               user_specified_dirs,
               environ,
               uid): # type (bool, List[str], Dict[str, str], int) -> Iterator[Tuple[str, TrashDir[str, str]]]
        if all_users_flag:
            for dir in self.all_users_dirs.scan_trash_dirs(environ, uid):
                yield dir
        else:
            if not user_specified_dirs:
                for dir in self.current_user_dirs.scan_trash_dirs(environ, uid):
                    yield dir
            for dir in user_specified_dirs:
                yield trash_dir_found, (
                    TrashDir(dir, self.volumes.volume_of(dir)))

    @staticmethod
    def make(volumes_listing,
             reader,  # type: TopTrashDirRules.Reader
             volumes  # type: Volumes
             ):
        user_info_provider = UserInfoProvider()
        user_dir_scanner = TrashDirsScanner(user_info_provider,
                                            volumes_listing,
                                            TopTrashDirRules(reader),
                                            DirChecker())
        all_users_info_provider = AllUsersInfoProvider()
        all_users_scanner = TrashDirsScanner(all_users_info_provider,
                                             volumes_listing,
                                             TopTrashDirRules(reader),
                                             DirChecker())
        return TrashDirsSelector(user_dir_scanner,
                                 all_users_scanner,
                                 volumes)


class Action(SuperEnum):
    debug_volumes = 'debug_volumes'
    print_version = 'print_version'
    list_trash = 'list_trash'
    list_volumes = 'list_volumes'
    list_trash_dirs = 'list_trash_dirs'
    print_python_executable = 'print_python_executable'


class Parser:
    def __init__(self, prog):
        self.parser = argparse.ArgumentParser(prog=prog,
                                              description='List trashed files',
                                              epilog='Report bugs to https://github.com/andreafrancia/trash-cli/issues')
        add_argument_to(self.parser)
        self.parser.add_argument('--version',
                                 dest='action',
                                 action='store_const',
                                 const=Action.print_version,
                                 default=Action.list_trash,
                                 help="show program's version number and exit")
        self.parser.add_argument('--debug-volumes',
                                 dest='action',
                                 action='store_const',
                                 const=Action.debug_volumes,
                                 help=argparse.SUPPRESS)
        self.parser.add_argument('--volumes',
                                 dest='action',
                                 action='store_const',
                                 const=Action.list_volumes,
                                 help="list volumes")
        self.parser.add_argument('--trash-dirs',
                                 dest='action',
                                 action='store_const',
                                 const=Action.list_trash_dirs,
                                 help="list trash dirs")
        self.parser.add_argument('--trash-dir',
                                 action='append',
                                 default=[],
                                 dest='trash_dirs',
                                 help='specify the trash directory to use'
                                 ).complete = TRASH_DIRS
        self.parser.add_argument('--size',
                                 action='store_const',
                                 default='deletion_date',
                                 const='size',
                                 dest='attribute_to_print',
                                 help=argparse.SUPPRESS)
        self.parser.add_argument('--files',
                                 action='store_true',
                                 default=False,
                                 dest='show_files',
                                 help=argparse.SUPPRESS)
        self.parser.add_argument('--all-users',
                                 action='store_true',
                                 dest='all_users',
                                 help='list trashcans of all the users')
        self.parser.add_argument('--python',
                                 dest='action',
                                 action='store_const',
                                 const=Action.print_python_executable,
                                 help=argparse.SUPPRESS)

    def parse_list_args(self, args):
        parsed = self.parser.parse_args(args)
        return parsed


class ListCmdOutput:
    def __init__(self, out, err):
        self.out = out
        self.err = err

    def println(self, line):
        self.out.write(line + '\n')

    def error(self, line):
        self.err.write(line + '\n')

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
