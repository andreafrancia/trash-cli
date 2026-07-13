from trashcli.fslib.real_fs_operations import RealExists, RealIsStickyDir, RealIsSymLink, \
    RealIsWorldWritable
from trashcli.trash_dirs_scanner import TopTrashDirRulesFs


class RealTopTrashDirFs(
    TopTrashDirRulesFs,
    RealExists,
    RealIsStickyDir,
    RealIsSymLink,
    RealIsWorldWritable,
):
    pass
