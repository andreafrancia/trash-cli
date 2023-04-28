from trashcli.list.extractors import DeletionDateExtractor, SizeExtractor
from trashcli.lib.trash_dir_reader import TrashDirReader
from trashcli.trash_dirs_scanner import trash_dir_found, \
    trash_dir_skipped_because_parent_not_sticky, \
    trash_dir_skipped_because_parent_is_symlink


class ListTrash:
    def __init__(self, environ, uid, selector, output, printer, file_reader):
        self.environ = environ
        self.uid = uid
        self.selector = selector
        self.output = output
        self.printer = printer
        self.file_reader = file_reader

    def execute(self, parsed):
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
                    self.printer.print_trashinfo(volume, trash_info,
                                                 extractor,
                                                 show_files)
            elif event == trash_dir_skipped_because_parent_not_sticky:
                path, = args
                self.output.top_trashdir_skipped_because_parent_not_sticky(
                    path)
            elif event == trash_dir_skipped_because_parent_is_symlink:
                path, = args
                self.output.top_trashdir_skipped_because_parent_is_symlink(
                    path)
