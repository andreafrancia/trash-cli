import os

import six

from trashcli.put.class_name_meta import ClassNameMeta


@six.add_metaclass(ClassNameMeta)
class CheckType:
    pass


class NoCheck(CheckType):
    pass


class TopTrashDirCheck(CheckType):
    pass


class SecurityCheck:

    def __init__(self, fs):
        self.fs = fs

    def check_trash_dir_is_secure(self, candidate):
        if candidate.check_type == NoCheck:
            return True, []
        if candidate.check_type == TopTrashDirCheck:
            parent = os.path.dirname(candidate.trash_dir_path)
            if not self.fs.isdir(parent):
                return False, [
                    "found unusable .Trash dir (should be a dir): %s" % parent]
            if self.fs.islink(parent):
                return False, [
                    "found unsecure .Trash dir (should not be a symlink): %s" % parent]
            if not self.fs.has_sticky_bit(parent):
                return False, [
                    "found unsecure .Trash dir (should be sticky): %s" % parent]
            return True, []
        raise Exception("Unknown check type: %s" % candidate.check_type)
