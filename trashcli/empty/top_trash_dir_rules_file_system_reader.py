from trashcli.fs import FsMethods
from trashcli.trash_dirs_scanner import TopTrashDirRules


class TopTrashDirRulesFileSystemReader(TopTrashDirRules.Reader):
    exists = FsMethods().exists
    is_sticky_dir = FsMethods().is_sticky_dir
    is_symlink = FsMethods().is_symlink
