from six import StringIO
from typing import List
from typing import Optional

from tests.support.put.dummy_clock import FixedClock
from tests.support.put.dummy_clock import jan_1st_2024
from tests.support.put.fake_random import FakeRandomInt
from tests.test_put.support.recording_backend import RecordingBackend
from tests.test_put.support.result import Result
from trashcli.lib.environ import Environ
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.main import make_cmd
from trashcli.put.parser import ensure_int


class PutUser:
    def __init__(self, fs):
        self.fs = fs
        self.user_input = HardCodedInput()
        self.ints = []

    def set_user_reply(self,
                       reply,  # type: str
                       ):
        self.user_input.set_reply(reply)

    def add_random_int(self, value):
        self.ints.append(value)

    def touch_and_trash(self, path):
        self.fs.touch(path)
        self.run_cmd(['trash-put', path])

    def last_user_prompt(self):
        return self.user_input.last_prompt()

    def run_cmd(self,
                args,  # type: List[str]
                environ=None,  # type: Optional[Environ]
                uid=None,  # type: Optional[int]
                ):  # type: (...) -> Result
        environ = environ or {}
        uid = uid or 123
        err = None
        exit_code = None
        stderr = StringIO()
        clock = FixedClock(jan_1st_2024())
        backend = RecordingBackend(stderr)
        cmd = make_cmd(clock=clock,
                       fs=self.fs,
                       user_input=self.user_input,
                       randint=FakeRandomInt(self.ints),
                       backend=backend)
        try:
            exit_code = cmd.run_put(args, environ, uid)
        except IOError as e:
            err = e
        stderr_lines = stderr.getvalue().splitlines()

        return Result(stderr_lines, str(err), ensure_int(exit_code),
                      backend.collected())
