from six import StringIO

from tests.support.put.dummy_clock import FixedClock, jan_1st_2024
from tests.support.put.fake_fs.failing_fake_fs import FailingFakeFs
from tests.support.put.fake_random import FakeRandomInt
from tests.test_put.support.recording_backend import RecordingBackend
from tests.test_put.support.result import Result
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.main import make_cmd
from trashcli.put.parser import ensure_int


class TestPutSymlinkedTrashDir:
    def setup_method(self):
        self.fs = FailingFakeFs()
        self.user_input = HardCodedInput('y')
        self.randint = FakeRandomInt([])

    def test_it_does_not_trash_into_a_symlinked_info_dir(self):
        self.fs.touch("/foo")
        self.fs.makedirs("/.Trash-123", 0o700)
        self.fs.symlink("/somewhere-else", "/.Trash-123/info")

        self.run_cmd(['trash-put', '/foo'])

        assert self.fs.exists("/foo")
        assert not self.fs.exists('/.Trash-123/files')

    def run_cmd(self, args):
        stderr = StringIO()
        backend = RecordingBackend(stderr)
        cmd = make_cmd(clock=FixedClock(jan_1st_2024()), fs=self.fs,
                       user_input=self.user_input, randint=self.randint,
                       backend=backend)
        exit_code = cmd.run_put(args, {}, 123)
        return Result(stderr.getvalue().splitlines(), "",
                      ensure_int(exit_code), backend.collected())
