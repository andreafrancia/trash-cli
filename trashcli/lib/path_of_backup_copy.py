from __future__ import absolute_import

import os


def path_of_backup_copy(trashinfo_path):
    trash_dir = os.path.dirname(os.path.dirname(trashinfo_path))
    basename = os.path.basename(trashinfo_path)[:-len('.trashinfo')]
    return os.path.join(trash_dir, 'files', basename)
