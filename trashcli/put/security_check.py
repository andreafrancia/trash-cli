import os


class SecurityCheck:
    def __init__(self, fs):
        self.fs = fs

    def check_trash_dir_is_secure(self, trash_dir_path, check_type):
        if check_type == all_is_ok_rules:
            return True, []
        if check_type == top_trash_dir_rules:
            parent = os.path.dirname(trash_dir_path)
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
        raise Exception("Unknown check type: %s" % check_type)


all_is_ok_rules = 'all_is_ok_rules'
top_trash_dir_rules = 'top_trash_dir_rules'
