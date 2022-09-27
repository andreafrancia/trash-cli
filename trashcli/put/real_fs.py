import os

from trashcli import fs


class RealFs:
    def __init__(self):
        self.move = fs.move
        self.atomic_write = fs.atomic_write
        self.remove_file = fs.remove_file
        self.ensure_dir = fs.ensure_dir
        self.isdir = os.path.isdir
        self.islink = os.path.islink
        self.has_sticky_bit = fs.has_sticky_bit
