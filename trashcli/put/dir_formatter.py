import os
import posixpath
import re


class DirFormatter:
    def __init__(self, environ):
        self.environ = environ

    def shrink_user(self, path):
        home_dir = self.environ.get('HOME', '')
        home_dir = posixpath.normpath(home_dir)
        if home_dir != '':
            path = re.sub('^' + re.escape(home_dir + os.path.sep),
                          '~' + os.path.sep, path)
        return path
