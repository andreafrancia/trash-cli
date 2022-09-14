from trashcli.trash_dirs_scanner import only_found, TrashDir


class Emptier:
    def __init__(self, delete_mode, trash_dir_reader, trashcan):
        self.delete_mode = delete_mode
        self.trash_dir_reader = trash_dir_reader
        self.trashcan = trashcan

    def do_empty(self, trash_dirs, environ, parsed_days):
        for trash_dir in only_found(trash_dirs):  # type: TrashDir
            for trash_info_path in self.trash_dir_reader.list_trashinfo(
                    trash_dir.path):
                if self.delete_mode.ok_to_delete(trash_info_path, environ,
                                                 parsed_days):
                    self.trashcan.delete_trashinfo_and_backup_copy(
                        trash_info_path)
            for orphan in self.trash_dir_reader.list_orphans(
                    trash_dir.path):
                self.trashcan.delete_orphan(orphan)
