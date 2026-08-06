from trashcli.fslib.real_fs_operations import RealExists, RealIsSymLink, \
    RealIsWorldWritable
from trashcli.fslib.real_is_sticky_dir import RealIsStickyDir
from trashcli.trash_dirs_scanner import TopTrashDirRulesFs


class RealTopTrashDirFs(
    TopTrashDirRulesFs,
    RealExists,
    RealIsStickyDir,
    RealIsSymLink,
    RealIsWorldWritable,
):
    pass
