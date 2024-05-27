from trashcli.fs_impl import RealIsSymLink
from trashcli.fs_impl import RealIsStickyDir
from trashcli.fs_impl import RealPathExists
from trashcli.trash_dirs_scanner import TopTrashDirRules


class RealTopTrashDirRulesReader(
    TopTrashDirRules.Reader,
    RealPathExists,
    RealIsStickyDir,
    RealIsSymLink,
):
    pass
