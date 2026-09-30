import os
import stat

from trashcli.fslib.protocols.is_world_writable import IsWorldWritable


class RealIsWorldWritable(IsWorldWritable):
    def is_world_writable(self, path):  # type: (str) -> bool
        try:
            return bool(os.stat(path).st_mode & stat.S_IWOTH)
        except OSError:
            return False
