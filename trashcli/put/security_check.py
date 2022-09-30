import os


class SecurityCheck:
    def check_trash_dir_is_secure(self, trash_dir_path, fs, check_type):
        checker = {top_trash_dir_rules: TopTrashDirRules(),
                   all_is_ok_rules: AllIsOkRules()}[check_type]
        return checker.check_trash_dir_is_secure(trash_dir_path, fs,
                                                 check_type)


class AllIsOkRules:
    def check_trash_dir_is_secure(self, trash_dir_path, fs, check_type):
        return True, []


class TopTrashDirRules:
    def check_trash_dir_is_secure(self, trash_dir_path, fs, check_type):
        parent = os.path.dirname(trash_dir_path)
        if not fs.isdir(parent):
            return False, [
                "found unusable .Trash dir (should be a dir): %s" % parent]
        if fs.islink(parent):
            return False, [
                "found unsecure .Trash dir (should not be a symlink): %s" % parent]
        if not fs.has_sticky_bit(parent):
            return False, [
                "found unsecure .Trash dir (should be sticky): %s" % parent]
        return True, []


all_is_ok_rules = 'all_is_ok_rules'
top_trash_dir_rules = 'top_trash_dir_rules'
