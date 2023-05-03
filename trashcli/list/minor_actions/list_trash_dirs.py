from typing import List, NamedTuple

from trashcli.trash_dirs_scanner import trash_dir_found, \
    trash_dir_skipped_because_parent_not_sticky, \
    trash_dir_skipped_because_parent_is_symlink


class ListTrashDirsArgs(
    NamedTuple('ListTrashDirsArgs',
               [('trash_dirs', List[str]),
                ('all_users', bool)])
):
    pass


class ListTrashDirs:
    def __init__(self, environ, uid, selector):
        self.environ = environ
        self.uid = uid
        self.selector = selector

    def run_action(self, args):
        user_specified_trash_dirs = args.trash_dirs
        all_users = args.all_users
        trash_dirs = self.selector.select(all_users,
                                          user_specified_trash_dirs,
                                          self.environ,
                                          self.uid)
        for event, event_args in trash_dirs:
            if event == trash_dir_found:
                path, volume = event_args
                print("%s" % path)
            elif event == trash_dir_skipped_because_parent_not_sticky:
                path = event_args
                print("parent_not_sticky: %s" % (path))
            elif event == trash_dir_skipped_because_parent_is_symlink:
                path = event_args
                print("parent_is_symlink: %s" % (path))
