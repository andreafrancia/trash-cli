import os
import random
import sys
from datetime import datetime

from trashcli.fstab import volumes
from trashcli.put.access import Access
from trashcli.put.clock import RealClock
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import MyLogger
from trashcli.put.original_location import OriginalLocation, parent_realpath
from trashcli.put.parent_path import parent_path
from trashcli.put.path_maker import PathMaker
from trashcli.put.real_fs import RealFs
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.suffix import Suffix
from trashcli.put.trash_all import TrashAll
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trash_put_cmd import TrashPutCmd
from trashcli.put.trasher import Trasher
from trashcli.put.user import User
from trashcli.trash import my_input


def main():
    logger = MyLogger(sys.stderr)
    reporter = TrashPutReporter(logger)
    fs = RealFs()
    suffix = Suffix(random.randint)
    info_dir = InfoDir(fs, logger, suffix)
    path_maker = PathMaker()
    original_location = OriginalLocation(parent_realpath, path_maker)
    trash_dir = TrashDirectoryForPut(fs,
                                     info_dir,
                                     original_location,
                                     RealClock())
    trash_file_in = TrashFileIn(fs,
                                os.path.realpath,
                                volumes,
                                datetime.now,
                                parent_path,
                                reporter,
                                info_dir,
                                trash_dir)
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
