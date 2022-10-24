import os
import random
import sys

import trashcli.fstab
import trashcli.trash
from trashcli.lib.my_input import my_input
from trashcli.put.clock import RealClock
from trashcli.put.describer import Describer
from trashcli.put.dir_maker import DirMaker
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.info_dir import InfoDir
from trashcli.put.my_logger import MyLogger
from trashcli.put.original_location import OriginalLocation
from trashcli.put.parent_realpath import ParentRealpath
from trashcli.put.path_maker import PathMaker
from trashcli.put.real_fs import RealFs
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.suffix import Suffix
from trashcli.put.trash_all import TrashAll
from trashcli.put.trash_dir_volume import TrashDirVolume
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trash_file_in import TrashFileIn
from trashcli.put.trash_put_cmd import TrashPutCmd
from trashcli.put.trasher import Trasher
from trashcli.put.user import User


def main():
    cmd = make_cmd(clock=RealClock(), fs=RealFs(),
                   my_input=my_input, randint=random.randint,
                   stderr=sys.stderr, volumes=trashcli.fstab.volumes)
    return cmd.run(sys.argv, os.environ, os.getuid())


def make_cmd(clock, fs, my_input, randint, stderr, volumes):
    logger = MyLogger(stderr)
    describer = Describer(fs)
    reporter = TrashPutReporter(logger, describer)
    suffix = Suffix(randint)
    dir_maker = DirMaker(fs)
    info_dir = InfoDir(fs, logger, suffix)
    path_maker = PathMaker()
    parent_realpath = ParentRealpath(fs)
    original_location = OriginalLocation(parent_realpath, path_maker)
    trash_dir = TrashDirectoryForPut(fs,
                                     info_dir,
                                     original_location,
                                     clock)
    trash_dir_volume = TrashDirVolume(volumes, fs)
    trash_file_in = TrashFileIn(fs,
                                reporter,
                                info_dir,
                                trash_dir,
                                trash_dir_volume,
                                dir_maker)
    file_trasher = FileTrasher(volumes,
                               TrashDirectoriesFinder(volumes),
                               parent_realpath,
                               logger,
                               reporter,
                               trash_file_in)
    user = User(my_input, describer)
    trasher = Trasher(file_trasher, user, reporter, fs)
    trash_all = TrashAll(logger, trasher)
    return TrashPutCmd(trash_all, reporter)
