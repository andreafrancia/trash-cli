from trashcli.trash_dirs_scanner import trash_dir_found, \
    trash_dir_skipped_because_parent_not_sticky, \
    trash_dir_skipped_because_parent_is_symlink


class ListTrashDirs:
    def __init__(self, environ, uid, selector):
        self.environ = environ
        self.uid = uid
        self.selector = selector

    def execute(self, parsed):
        user_specified_trash_dirs = parsed.trash_dirs
        all_users = parsed.all_users
        trash_dirs = self.selector.select(all_users,
                                          user_specified_trash_dirs,
                                          self.environ,
                                          self.uid)
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
