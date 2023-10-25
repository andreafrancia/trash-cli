import os
import random
import sys

from trashcli.fstab.volume_of import RealVolumeOf
from trashcli.lib.environ import cast_environ
from trashcli.lib.my_input import Input
from trashcli.lib.my_input import RealInput
from trashcli.put.clock import RealClock
from trashcli.put.core.int_generator import IntGenerator
from trashcli.put.describer import Describer
from trashcli.put.dir_maker import DirMaker
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.fs.fs import Fs
from trashcli.put.fs.parent_realpath import ParentRealpathFs
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.fs.volume_of_parent import VolumeOfParent
from trashcli.put.info_dir import PersistingInfoDir, InfoDir2
from trashcli.put.my_logger import MyLogger
from trashcli.put.original_location import OriginalLocation
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.suffix import Suffix
from trashcli.put.trash_all import TrashAll
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_directory_for_put import TrashDirectoryForPut
from trashcli.put.trash_file_in import Janitor
from trashcli.put.trash_put_cmd import TrashPutCmd
from trashcli.put.trasher import Trasher
from trashcli.put.trashing_checker import TrashDirChecker
from trashcli.put.user import User


def main():
    cmd = make_cmd(clock=RealClock(),
                   fs=RealFs(),
                   user_input=RealInput(),
                   randint=RandomIntGenerator(),
                   stderr=sys.stderr,
                   volumes=RealVolumeOf())
    return cmd.run_put(sys.argv, cast_environ(os.environ), os.getuid())


def make_cmd(clock,
             fs,  # type: Fs
             user_input,  # type: Input
             randint,  # type: IntGenerator
             stderr,
             volumes,
             ):  # type: (...) -> TrashPutCmd
    logger = MyLogger(stderr)
    describer = Describer(fs)
    reporter = TrashPutReporter(logger, describer)
    suffix = Suffix(randint)
    dir_maker = DirMaker(fs)
    info_dir = PersistingInfoDir(fs, logger, suffix)
    original_location = OriginalLocation(fs)
    info_dir2 = InfoDir2(info_dir, original_location, clock)
    trash_dir = TrashDirectoryForPut(fs, info_dir2)
    trashing_checker = TrashDirChecker(fs, volumes)
    trash_file_in = Janitor(fs,
                            reporter,
                            trash_dir,
                            trashing_checker,
                            dir_maker,
                            info_dir2)
    volume_of_parent = VolumeOfParent(volumes, ParentRealpathFs(fs))
    file_trasher = FileTrasher(volumes,
                               TrashDirectoriesFinder(volumes),
                               ParentRealpathFs(fs),
                               logger,
                               reporter,
                               trash_file_in,
                               volume_of_parent)
    user = User(user_input, describer)
    trasher = Trasher(file_trasher, user, reporter, fs)
    trash_all = TrashAll(logger, trasher)
    return TrashPutCmd(trash_all, reporter)


class RandomIntGenerator(IntGenerator):
    def new_int(self,
                min,  # type: int
                max,  # type: int
                ):
        return random.randint(min, max)
