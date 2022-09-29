import os
import sys
from datetime import datetime

from trashcli.fstab import volumes
from trashcli.put.access import Access
from trashcli.put.file_trasher import FileTrasher, TrashFileIn
from trashcli.put.my_logger import MyLogger
from trashcli.put.parent_path import parent_path
from trashcli.put.real_fs import RealFs
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.trash_all import TrashAll
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trasher import Trasher
from trashcli.put.user import User
from trashcli.trash import my_input
from trashcli.put.trash_put_cmd import TrashPutCmd


def main():
    logger = MyLogger(sys.stderr)
    reporter = TrashPutReporter(logger)
    fs = RealFs()
    trash_file_in = TrashFileIn(fs,
                                os.path.realpath,
                                volumes,
                                datetime.now,
                                parent_path,
                                logger,
                                reporter)
    file_trasher = FileTrasher(fs,
                               volumes,
                               os.path.realpath,
                               datetime.now,
                               TrashDirectoriesFinder(volumes),
                               parent_path,
                               logger,
                               reporter,
                               trash_file_in)
    access = Access()
    user = User(my_input)
    trasher = Trasher(file_trasher, user, access, reporter)
    trash_all = TrashAll(logger, trasher)
    cmd = TrashPutCmd(trash_all, reporter)
    return cmd.run(sys.argv, os.environ, os.getuid())
