import os
import random
import sys

from trashcli.lib.environ import cast_environ
from trashcli.lib.my_input import Input
from trashcli.lib.my_input import RealInput
from trashcli.put.clock import RealClock
from trashcli.put.core.int_generator import IntGenerator
from trashcli.put.describer import Describer
from trashcli.put.file_trasher import FileTrasher
from trashcli.put.fs.fs import Fs
from trashcli.put.fs.real_fs import RealFs
from trashcli.put.janitor import Janitor
from trashcli.put.my_logger import LoggerBackend
from trashcli.put.my_logger import StreamBackend
from trashcli.put.reporting.trash_put_reporter import TrashPutReporter
from trashcli.put.trash_put_cmd import TrashPutCmd
from trashcli.put.trasher import Trasher
from trashcli.put.user import User


def main():
    cmd = make_cmd(clock=RealClock(),
                   fs=RealFs(),
                   user_input=RealInput(),
                   randint=RandomIntGenerator(),
                   backend=StreamBackend(sys.stderr))
    try:
        uid = int(os.environ["TRASH_PUT_FAKE_UID_FOR_TESTING"])
    except KeyError:
        uid = os.getuid()
    return cmd.run_put(sys.argv, cast_environ(os.environ), uid)


def make_cmd(clock,
             fs,  # type: Fs
             user_input,  # type: Input
             randint,  # type: IntGenerator
             backend,  # type: LoggerBackend
             ):  # type: (...) -> TrashPutCmd
    reporter = TrashPutReporter(fs)
    janitor = Janitor(fs, clock, backend, randint)
    file_trasher = FileTrasher(fs, janitor, backend)
    user = User(user_input, Describer(fs))
    trasher = Trasher(file_trasher, user, fs, backend)
    return TrashPutCmd(reporter, trasher)


class RandomIntGenerator(IntGenerator):
    def new_int(self,
                min,  # type: int
                max,  # type: int
                ):
        return random.randint(min, max)
