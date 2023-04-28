from __future__ import absolute_import

import os


class DirChecker:
    @staticmethod
    def is_dir(path):
        return os.path.isdir(path)
