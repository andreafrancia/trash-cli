import errno

from six import StringIO

from tests.support.put.dummy_clock import FixedClock, jan_1st_2024
from tests.support.put.fake_fs.failing_fake_fs import FailingFakeFs
from tests.support.put.fake_random import FakeRandomInt
from tests.test_put.support.recording_backend import RecordingBackend
from tests.test_put.support.result import Result
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.main import make_cmd
from trashcli.put.parser import ensure_int


class TestPutUnwritableTrashDir:
    def setup_method(self):
        self.fs = FailingFakeFs()
        self.user_input = HardCodedInput('y')
        self.randint = FakeRandomInt([])

    def test_it_reports_an_error_when_the_trashinfo_cannot_be_written(self):
        self.fs.touch("/foo")
        self.fs.fail_atomic_write_with_errno(errno.EACCES)

        result = self.run_cmd(['trash-put', '/foo'])

        assert result.exit_code == EX_IOERR
        assert any('Permission denied' in line for line in result.stderr), \
            result.stderr

    def test_it_leaves_the_original_file_in_place_on_failure(self):
        self.fs.touch("/foo")
        self.fs.fail_atomic_write_with_errno(errno.EACCES)

        self.run_cmd(['trash-put', '/foo'])

        assert self.fs.exists("/foo")

    def test_it_does_not_move_the_file_into_the_trash_on_failure(self):
        self.fs.touch("/foo")
        self.fs.fail_atomic_write_with_errno(errno.EROFS)

        self.run_cmd(['trash-put', '/foo'])

        assert self.fs.ls_aa('/.Trash-123/files') == []

    def run_cmd(self, args):
        stderr = StringIO()
        backend = RecordingBackend(stderr)
        cmd = make_cmd(clock=FixedClock(jan_1st_2024()), fs=self.fs,
                       user_input=self.user_input, randint=self.randint,
                       backend=backend)
        exit_code = cmd.run_put(args, {}, 123)
        return Result(stderr.getvalue().splitlines(), "",
                      ensure_int(exit_code), backend.collected())
