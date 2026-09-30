from trashcli.fslib.real.real_exists import RealExists
from trashcli.fslib.real.real_is_sticky_dir import RealIsStickyDir
from trashcli.fslib.real.real_is_sym_link import RealIsSymLink
from trashcli.fslib.real.real_is_world_writable import RealIsWorldWritable
from trashcli.trash_dirs_scanner import TopTrashDirRulesFs


class RealTopTrashDirFs(
    TopTrashDirRulesFs,
    RealExists,
    RealIsStickyDir,
    RealIsSymLink,
    RealIsWorldWritable,
):
    pass
