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
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.fs.fs import Fs
from trashcli.put.fs.parent_realpath import ParentRealpathFs
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.fs.volume_of_parent import VolumeOfParent
from trashcli.put.janitor import Janitor
from trashcli.put.janitor_tools.info_creator import \
    TrashInfoCreator
from trashcli.put.janitor_tools.info_file_persister import InfoFilePersister
from trashcli.put.janitor_tools.put_trash_dir import PutTrashDir
from trashcli.put.janitor_tools.trash_dir_checker import TrashDirChecker
from trashcli.put.my_logger import MyLogger
from trashcli.put.original_location import OriginalLocation
from trashcli.put.reporter import TrashPutReporter
from trashcli.put.suffix import Suffix
from trashcli.put.trash_all import TrashAll
from trashcli.put.trash_directories_finder import TrashDirectoriesFinder
from trashcli.put.trash_put_cmd import TrashPutCmd
from trashcli.put.trasher import Trasher
from trashcli.put.user import User


def main():
    cmd = make_cmd(clock=RealClock(),
                   fs=RealFs(),
                   user_input=RealInput(),
                   randint=RandomIntGenerator(),
                   stderr=sys.stderr,
                   volumes=RealVolumeOf())
    try:
        uid = int(os.environ["TRASH_PUT_FAKE_UID_FOR_TESTING"])
    except KeyError:
        uid = os.getuid()
    return cmd.run_put(sys.argv, cast_environ(os.environ), uid)


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
    persister = InfoFilePersister(fs, logger, suffix)
    original_location = OriginalLocation(fs)
    info_dir2 = TrashInfoCreator(persister, original_location, clock)
    trash_dir = PutTrashDir(fs, info_dir2)
    trashing_checker = TrashDirChecker(fs, volumes)
    janitor = Janitor(fs,
                      trash_dir,
                      trashing_checker,
                      info_dir2,
                      persister,
                      logger)
    volume_of_parent = VolumeOfParent(volumes, ParentRealpathFs(fs))
    file_trasher = FileTrasher(volumes,
                               TrashDirectoriesFinder(volumes),
                               ParentRealpathFs(fs),
                               logger,
                               reporter,
                               janitor,
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
