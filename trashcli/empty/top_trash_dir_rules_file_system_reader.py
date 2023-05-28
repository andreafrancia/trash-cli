from trashcli.fs import RealExists, RealIsStickyDir, RealIsSymLink
from trashcli.trash_dirs_scanner import TopTrashDirRules


class TopTrashDirRulesFileSystemReader(
    TopTrashDirRules.Reader,
    RealExists,
    RealIsStickyDir,
    RealIsSymLink,
):
    pass
