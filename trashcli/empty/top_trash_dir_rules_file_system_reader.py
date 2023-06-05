from trashcli.fs import RealExists, RealIsStickyDir, RealIsSymLink
from trashcli.trash_dirs_scanner import TopTrashDirRules


class RealTopTrashDirRulesReader(
    TopTrashDirRules.Reader,
    RealExists,
    RealIsStickyDir,
    RealIsSymLink,
):
    pass
