from trashcli.fslib.real_fs_operations import RealExists, RealIsStickyDir, RealIsSymLink, \
    RealIsWorldWritable
from trashcli.trash_dirs_scanner import TopTrashDirRules


class RealTopTrashDirFs(
    TopTrashDirRules.Reader,
    RealExists,
    RealIsStickyDir,
    RealIsSymLink,
    RealIsWorldWritable,
):
    pass
