import os
import random
import sys

import trashcli.fstab
from trashcli.put.access import Access
from trashcli.put.clock import RealClock
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.trash_dir_volume import TrashDirVolume
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import MyLogger
from trashcli.put.original_location import OriginalLocation
from trashcli.put.parent_realpath import ParentRealpath
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
import trashcli.trash


def main():
    return do_main(access=Access(), argv=sys.argv, clock=RealClock(),
                   environ=os.environ, fs=RealFs(),
                   my_input=trashcli.trash.my_input, randint=random.randint,
                   realpath=os.path.realpath, stderr=sys.stderr,
                   uid=os.getuid(), volumes=trashcli.fstab.volumes)


def do_main(access, argv, clock, environ, fs, my_input, randint, realpath,
            stderr, uid, volumes):
    logger = MyLogger(stderr)
    reporter = TrashPutReporter(logger)
    suffix = Suffix(randint)
    info_dir = InfoDir(fs, logger, suffix)
    path_maker = PathMaker()
    parent_realpath = ParentRealpath(realpath)
    original_location = OriginalLocation(parent_realpath, path_maker)
    trash_dir = TrashDirectoryForPut(fs,
                                     info_dir,
                                     original_location,
                                     clock)
    trash_dir_volume = TrashDirVolume(volumes, realpath)
    trash_file_in = TrashFileIn(fs,
                                reporter,
                                info_dir,
                                trash_dir,
                                trash_dir_volume)
    file_trasher = FileTrasher(volumes,
                               TrashDirectoriesFinder(volumes),
                               parent_realpath,
                               logger,
                               reporter,
                               trash_file_in)
    user = User(my_input)
    trasher = Trasher(file_trasher, user, access, reporter)
    trash_all = TrashAll(logger, trasher)
    cmd = TrashPutCmd(trash_all, reporter)
    return cmd.run(argv, environ, uid)
