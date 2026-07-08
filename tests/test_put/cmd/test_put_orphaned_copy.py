from tests.support.put.fake_fs.failing_fake_fs import FailingFakeFs
from tests.support.put.fake_random import FakeRandomInt
from tests.test_put.support.recording_backend import RecordingBackend
from six import StringIO
from tests.support.put.dummy_clock import FixedClock, jan_1st_2024
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.main import make_cmd


class TestPutOrphanedCopy:
    def setup_method(self):
        self.fs = FailingFakeFs()
        self.user_input = HardCodedInput('y')
        self.randint = FakeRandomInt([])

    def test_a_file_that_cannot_be_removed_is_not_left_as_a_copy(self):
        self.fs.touch("/foo")
        # the move copies the file into the trash then fails to delete the original
        self.fs.fail_move_leaving_copy_on("/foo")

        self.run_cmd(['trash-put', '/foo'])

        assert self.fs.exists("/foo")
        assert self.fs.ls_aa('/.Trash-123/files') == []
        assert self.fs.ls_aa('/.Trash-123/info') == []

    def run_cmd(self, args):
        cmd = make_cmd(clock=FixedClock(jan_1st_2024()), fs=self.fs,
                       user_input=self.user_input, randint=self.randint,
                       backend=RecordingBackend(StringIO()))
        return cmd.run_put(args, {}, 123)
