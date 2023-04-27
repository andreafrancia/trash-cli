import os

from trashcli.fs import FileSystemReader
from trashcli.fstab import Volumes
from trashcli.list.actions import Action
from trashcli.list.cmd_output import ListCmdOutput
from trashcli.list.extractors import DeletionDateExtractor, SizeExtractor
from trashcli.list.parser import Parser
from trashcli.list.subcmds.debug_volumes import DebugVolumesSubCmd
from trashcli.list.subcmds.list_volumes import PrintVolumesList
from trashcli.list.trash_dir_selector import TrashDirsSelector
from trashcli.trash import version, print_version, TrashDirReader, parse_path, \
    ParseError, path_of_backup_copy
from trashcli.trash_dirs_scanner import trash_dir_found, \
    trash_dir_skipped_because_parent_not_sticky, \
    trash_dir_skipped_because_parent_is_symlink


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
            PrintVolumesList(self.environ, self.volumes_listing).exectute()
        elif parsed.action == Action.debug_volumes:
            DebugVolumesSubCmd().execute()
        elif parsed.action == Action.list_trash_dirs:
            self.list_trash_dirs(parsed.trash_dirs,
                                 parsed.all_users,
                                 self.environ,
                                 self.uid)
        elif parsed.action == Action.list_trash:
            self.list_trash(parsed)
        elif parsed.action == Action.print_python_executable:
            self.print_python_executable()
        else:
            raise ValueError('Unknown action: ' + parsed.action)

    class ListTrashSubCmd:
        def __init__(self, environ, uid, selector):
            self.environ = environ
            self.uid = uid
            self.selector = selector

        def execute(self, parsed):
            pass

    def list_trash(self, parsed):
        cmd = self.ListTrashSubCmd(self.environ, self.uid, self.selector)
        cmd.execute(parsed)
        extractors = {
            'deletion_date': DeletionDateExtractor(),
            'size': SizeExtractor(),
        }
        user_specified_trash_dirs = parsed.trash_dirs
        extractor = extractors[parsed.attribute_to_print]
        show_files = parsed.show_files
        all_users = parsed.all_users
        trash_dirs = self.selector.select(all_users,
                                          user_specified_trash_dirs,
                                          self.environ,
                                          self.uid)
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


def format_line(attribute, original_location):
    return "%s %s" % (attribute, original_location)


def format_line2(attribute, original_location, original_file):
    return "%s %s -> %s" % (attribute, original_location, original_file)
