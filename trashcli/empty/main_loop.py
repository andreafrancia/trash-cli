from trashcli.trash import trash_dir_found


class MainLoop:
    def __init__(self, trash_dir_reader, trashcan):
        self.trash_dir_reader = trash_dir_reader
        self.trashcan = trashcan

    def do_loop(self, trash_dirs, delete_mode, environ, parsed_days):
        for event, args in trash_dirs:
            if event == trash_dir_found:
                trash_dir_path, volume = args
                for trashinfo_path in self.trash_dir_reader.list_trashinfo(
                        trash_dir_path):
                    if delete_mode.ok_to_delete(trashinfo_path, environ,
                                                parsed_days):
                        self.trashcan.delete_trashinfo_and_backup_copy(
                            trashinfo_path)
                for orphan in self.trash_dir_reader.list_orphans(
                        trash_dir_path):
                    self.trashcan.delete_orphan(orphan)
