import os

from trashcli.put.fs.real_fs import RealFs


class Describer:
    def __init__(self, fs):
        self.fs = fs

    def describe(self, path):
        """
        Return a textual description of the file pointed by this path.
        Options:
         - "symbolic link"
         - "directory"
         - "'.' directory"
         - "'..' directory"
         - "regular file"
         - "regular empty file"
         - "non existent"
         - "entry"
        """
        if self.fs.islink(path):
            return 'symbolic link'
        elif self.fs.isdir(path):
            if path == '.':
                return 'directory'
            elif path == '..':
                return 'directory'
            else:
                if os.path.basename(path) == '.':
                    return "'.' directory"
                elif os.path.basename(path) == '..':
                    return "'..' directory"
                else:
                    return 'directory'
        elif self.fs.isfile(path):
            if self.fs.getsize(path) == 0:
                return 'regular empty file'
            else:
                return 'regular file'
        elif not self.fs.exists(path):
            return 'non existent'
        else:
            return 'entry'
