from six import StringIO

from tests.support.put.fake_fs.fake_fs import FakeFs
from tests.support.put.fake_random import FakeRandomInt
from tests.test_put.support.recording_backend import RecordingBackend
from tests.support.put.dummy_clock import FixedClock, jan_1st_2024
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.main import make_cmd


class TestPutRefusesUndeletableFile:
    def setup_method(self):
        self.fs = FakeFs()
        self.user_input = HardCodedInput('y')
        self.randint = FakeRandomInt([])

    def test_a_file_that_cannot_be_deleted_is_not_trashed_or_copied(self):
        self.fs.makedirs('/readonly', 0o755)
        self.fs.make_file('/readonly/foo', '')
        # the parent is not writable, so foo cannot be deleted by the user
        self.fs.chmod('/readonly', 0o500)

        self.run_cmd(['trash-put', '/readonly/foo'])

        assert self.fs.exists('/readonly/foo')
        assert not self.fs.exists('/.Trash-123/files/foo')
        assert not self.fs.exists('/.Trash-123/info/foo.trashinfo')

    def run_cmd(self, args):
        cmd = make_cmd(clock=FixedClock(jan_1st_2024()), fs=self.fs,
                       user_input=self.user_input, randint=self.randint,
                       backend=RecordingBackend(StringIO()))
        return cmd.run_put(args, {}, 123)
