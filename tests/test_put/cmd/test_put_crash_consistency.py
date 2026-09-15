import errno
import os

import pytest
from six import StringIO

from tests.support.put.dummy_clock import FixedClock
from tests.support.put.dummy_clock import jan_1st_2024
from tests.support.put.fake_fs.failing_fake_fs import FailingFakeFs
from tests.support.put.fake_random import FakeRandomInt
from tests.test_put.support.recording_backend import RecordingBackend
from trashcli.lib.exit_codes import EX_IOERR
from trashcli.lib.exit_codes import EX_OK
from trashcli.lib.my_input import HardCodedInput
from trashcli.put.main import make_cmd
from trashcli.put.parser import ensure_int

TRASH_DIR = "/.Trash-123"


class FakeProcessCrash(BaseException):
    """Simulates the death of the process: no error handling or cleanup runs."""


class CrashOnMoveFakeFs(FailingFakeFs):
    def __init__(self):
        super(CrashOnMoveFakeFs, self).__init__()
        self.info_dir_at_crash = None
        self.files_dir_at_crash = None

    def move(self, src, dest):
        trash_dir = os.path.dirname(os.path.dirname(dest))
        self.info_dir_at_crash = self.ls_aa(os.path.join(trash_dir, "info"))
        self.files_dir_at_crash = self.ls_aa(os.path.join(trash_dir, "files"))
        raise FakeProcessCrash()


class CrashOnAtomicWriteFakeFs(FailingFakeFs):
    def atomic_write(self, path, content):
        raise FakeProcessCrash()


class FailFirstAtomicWriteWithFakeFs(FailingFakeFs):
    def __init__(self, errno_value):
        super(FailFirstAtomicWriteWithFakeFs, self).__init__()
        self._errno_value = errno_value
        self._failures_left = 1

    def atomic_write(self, path, content):
        if self._failures_left:
            self._failures_left -= 1
            raise OSError(self._errno_value,
                          os.strerror(self._errno_value))
        return super(FailFirstAtomicWriteWithFakeFs, self). \
            atomic_write(path, content)


class TestPutCrashConsistency:
    def test_crash_between_trashinfo_write_and_file_move_leaves_no_orphan(
            self):
        fs = CrashOnMoveFakeFs()
        fs.touch("/foo")

        with pytest.raises(FakeProcessCrash):
            self.run_put(fs, ["trash-put", "/foo"])

        assert fs.info_dir_at_crash == []
        assert fs.files_dir_at_crash == []
        assert [] == fs.ls_aa(TRASH_DIR + "/info")
        assert [] == fs.ls_aa(TRASH_DIR + "/files")
        assert fs.exists("/foo")

    def test_crash_after_file_move_leaves_the_file_in_files_dir(self):
        fs = CrashOnAtomicWriteFakeFs()
        fs.touch("/foo")

        with pytest.raises(FakeProcessCrash):
            self.run_put(fs, ["trash-put", "/foo"])

        assert ["foo"] == fs.ls_aa(TRASH_DIR + "/files")
        assert [] == fs.ls_aa(TRASH_DIR + "/info")
        assert not fs.exists("/foo")

    def test_when_trashinfo_persistence_fails_after_the_move(self):
        fs = FailingFakeFs()
        fs.touch("/foo")
        fs.fail_atomic_write_with_errno(errno.ENOSPC)

        exit_code, stderr = self.run_put(fs, ["trash-put", "/foo"],
                                         {"HOME": "/home/user"})

        assert EX_IOERR == exit_code
        assert not fs.exists("/foo")
        assert ["foo"] == fs.ls_aa("/home/user/.local/share/Trash/files")
        assert [] == fs.ls_aa("/home/user/.local/share/Trash/info")
        assert any("failed to create trashinfo file" in line
                   for line in stderr)

    def test_when_trashinfo_name_is_too_long_the_pair_stays_in_sync(self):
        fs = FailFirstAtomicWriteWithFakeFs(errno.ENAMETOOLONG)
        fs.touch("/foo")

        exit_code, stderr = self.run_put(fs, ["trash-put", "/foo"])

        assert EX_OK == exit_code
        assert ["_1"] == fs.ls_aa(TRASH_DIR + "/files")
        assert ["_1.trashinfo"] == fs.ls_aa(TRASH_DIR + "/info")
        assert not fs.exists("/foo")

    def run_put(self,
                fs,
                args,
                environ=None,
                uid=None,
                ):
        environ = environ or {}
        uid = uid or 123
        stderr = StringIO()
        clock = FixedClock(jan_1st_2024())
        backend = RecordingBackend(stderr)
        cmd = make_cmd(clock=clock,
                       fs=fs,
                       user_input=HardCodedInput("y"),
                       randint=FakeRandomInt([]),
                       backend=backend)
        exit_code = cmd.run_put(args, environ, uid)

        return ensure_int(exit_code), stderr.getvalue().splitlines()
